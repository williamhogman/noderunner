"""
Python module for running node.js code from python
"""
import subprocess
import os.path
import json
import threading
from itertools import imap
import multiprocessing

import tornado.ioloop



_file = os.path.abspath(__file__)
_folder = os.path.dirname(_file)

_nr = os.path.join(_folder,"noderunner.js")

_sep = "\0"

class NodeProcess(object):
    def __init__(self,ioloop=tornado.ioloop.IOLoop.instance(),callback=None):
        self._proc = None
        self._bfr = str()
        self._ioloop = ioloop
        self._callback = callback

    def launch(self):
        self._proc = subprocess.Popen(_nr,
                                      bufsize=0,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        self._ioloop.add_handler(self._proc.stdout.fileno(),
                                self.read,
                                self._ioloop.READ)

    def send(self,obj):
        self._proc.stdin.write(json.dumps(obj)+_sep)
        self._proc.stdin.flush()

    def read(self,fd,event):
        data = self._proc.stdout.read(1)
        if _sep in data:
            cmds = (self._bfr + data).split(_sep)
            if len(cmds) == 1:
                self._bfr = cmds[0]
                return
            else:
                self._bfr = cmds[-1]
                self._callback(imap(json.loads,cmds[0:-1]))
        else:
            self._bfr = self._bfr + data

    def stop(self):
        self._proc.terminate()

class Node(object):
    def __init__(self):
        self._np = NodeProcess(callback=self._read)
        self._counter = 0
        self._resp_handlers = dict()
        self._status = False
        self._running = False

    def _read(self,data):
        for obj in data:
            if 'resp_to' in obj:
                resp = self._resp_handlers.get(obj['resp_to'])
                if 'err' in obj:
                    resp(err=obj['err'])
                elif 'data' in obj:
                    resp(data=obj['data'])
                elif 'status' in obj:
                    self._status = True
            
            
    def _write_msg(self,kind,data,callback):
        self._counter += 1
        c = self._counter
        self._resp_handlers[c] = callback
        self._np.send(dict(id=c,kind=kind,data=data))

    def eval(self,js,callback):
        def _inner(data=None,err=None):
            if err:
                callback(err=err)
            else:
                callback(data)
                
        self._write_msg('eval',js,_inner)

    def run(self):
        if not self._running:
            self._np.launch()
            self._running = True
    
class BlockingNode(object):
    def __init__(self):
        self._node = Node()
        self.il = tornado.ioloop.IOLoop.instance()
        self._results = None

    def eval(self,code):
        self._node.run()
        def _cb(data=None,err=None):
            self._results = (data,err)
            self.il.stop()
            
        self._node.eval(code,callback=_cb)
        self.il.start()
        return self._results

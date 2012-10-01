"""
Python module for running node.js code from python
"""
import subprocess
import os
import os.path
import json
from itertools import imap

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
        folder = os.path.join(_folder,"..","..",
                              "virtualenv","lib",
                              "node_modules")
        folder = os.path.abspath(folder)
        os.environ['NODE_PATH'] = ":".join(
            os.environ['NODE_PATH'].split(":") + [folder])

    def launch(self):
        self._proc = subprocess.Popen(_nr,
                                      bufsize=0,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        self._ioloop.add_handler(self._proc.stdout.fileno(),
                                 self.read,
                                 self._ioloop.READ)

    def send(self,obj):
        self._proc.stdin.write(json.dumps(obj) + _sep)
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
                try:
                    self._callback(imap(json.loads,cmds[0:-1]))
                except:
                    print("Crashed on {}".format(cmds))
                    raise
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

    def _mkcb(self,actual_cb):
        def _inner(data=None,err=None):
            if err:
                actual_cb(err=err)
            else:
                actual_cb(data=data)
        return _inner

    def eval(self,js,callback):
        # If we got a bunch of whitespace don't send it...
        if not js.strip():
            callback(None)
            return
        self._write_msg('eval',js,self._mkcb(callback))

    def call(self,fn,args,callback):
        if not fn.strip():
            callback(None)
            return
        self._write_msg('call',dict(path=fn,args=args),self._mkcb(callback))

    def require(self,name,path=None,callback=None):
        if path is None:
            sendobj = name
        else:
            sendobj = [name,path]
        self._write_msg('require',sendobj,self._mkcb(callback))

    def eval_async(self,js,callback):
        if not js.strip():
            callback(None)
            return
        self._write_msg('eval_async',js,self._mkcb(callback))

    def call_async(self,fn,args,callback=None):
        self._write_msg(
            'call_async',dict(path=fn,args=args),self._mkcb(callback))

    def run(self):
        if not self._running:
            self._np.launch()
            self._running = True


class BlockingNode(object):
    _instance = None

    def __init__(self):
        self._node = Node()
        self.il = tornado.ioloop.IOLoop.instance()
        self._results = None

    def _cb(self,data=None,err=None):
        self._results = (data,err)
        self.il.stop()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = BlockingNode()
        return cls._instance

    def wait(self):
        self.il.start()

    def eval(self,code):
        self._node.run()
        self._node.eval(code,callback=self._cb)

        self.wait()
        return self._results

    def call(self,name,*args):
        self._node.run()
        self._node.call(name,args,callback=self._cb)
        self.wait()
        return self._results

    def require(self,name,path=None):
        self._node.run()
        self._node.require(name,path,callback=self._cb)
        self.wait()
        return self._results

    def eval_async(self,name):
        self._node.run()
        self._node.eval_async(name,callback=self._cb)
        self.wait()
        return self._results

    def call_async(self,name,*args):
        self._node.run()
        self._node.call_async(name,args,callback=self._cb)
        self.wait()
        return self._results


def call(*args,**kwargs):
    return BlockingNode.instance().call(*args,**kwargs)


def eval(*args,**kwargs):
    return BlockingNode.instance().eval(*args,**kwargs)


def require(*args,**kwargs):
    return BlockingNode.instance().require(*args,**kwargs)

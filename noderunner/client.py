"""Client classes for noderunner"""
from noderunner.connection import Connection
from noderunner.protocol import Protocol
from noderunner.process import open_process
from noderunner.socket import get_sockets

class Client(object):

    def __init__(self, secured=False):
        self._secured = secured
        self._start()

    def _start(self):
        serv, cli, clifd = get_sockets()
        secret = "__NO_AUTH__"
        if self._secured:
            raise RuntimeError("Secure connections are not supported yet")

        self._proc = open_process(clifd, secret)
        self._con = Connection(serv)
        self._proto = Protocol(self._con,
                               None if not self._secured else secret)
        self._proto.start()

    def eval(self, code):
        return self._proto.request_sync("eval", code=code)

    def stop(self):
        self._proto.stop()
        self._proc.terminate()

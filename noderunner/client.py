"""Client classes for noderunner"""
from noderunner.connection import Connection
from noderunner.protocol import Protocol
from noderunner.process import open_process
from noderunner.socket import get_sockets


class Client(object):
    """Primary class for interfacing with node

    The client class provides an easy to use interface for calling
    node functions, handling context and requirements.
    """

    def __init__(self, secured=False):
        """Spawns a new node process and sets up communication"""
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

    def eval(self, code, context=None):
        """Evaluates the code and returns the result

        Evaluates the passed in string as JavaScript code. This code
        may optionally be run in a context.

        :param code: The code to be evaluated
        :type code: str.
        :param context: Name of the context to run the code in.
        :type context: str.
        :return: The result of evaluating the expression, as best
                 represented in python.
        """

        return self._proto.request_sync("eval", code=code, context=context)

    def stop(self):
        """Stops the client and terminates the node process"""
        self._proto.stop()
        self._proc.terminate()

    def context(self, name, reqs=[]):
        """Creates a named context

        Creates a named context with the passed in requirements
        pre-included, the context will have it's own global object
        making it hard to interfere with other things running in node.

        :param name: Name of the context to be created
        :type name: str.
        :param reqs: The names of the requirements to be loaded into
                     the context.
        :type reqs: list.
        :return: a context object for interfacing with it
        """
        name = self._proto.request_sync("mkcontext",
                                        name=name,
                                        requirements=reqs)
        return Context(self, name)


class Context(object):
    """A context in which certain commands such as eval can be run"""

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def eval(self, code):
        return self._client.eval(code, context=self._name)

"""Module for managing node.js processes

This module contains functions for managing processes owned by
noderunner. It is mostly just a thin wrapper arround Popen.
"""
from six.moves import map
import os
import subprocess


def _find_mainjs():
    moduledir = os.path.split(__file__)[0]
    return os.path.join(moduledir, "js", "main.js")


def _run_node(nodepath="node", *args):
    to_call = [nodepath, _find_mainjs()]
    to_call.extend(map(str, args))
    return subprocess.Popen(to_call, bufsize=0)


def open_process(server_fd, secret, nodepath="node"):
    """Opens a node process

    Spawns a new node.js process passing on the FD to be used by node
    secret should be a secret or the magic string "_NO_AUTH_" which
    disables the authentication process. The caller optionally pass in
    a path to the node server executable, if this option is missing
    the default 'node' is used.

    :param server_fd: The file descriptor the process should connect to.
    :type server_fd: int

    :param secret: The secret to be used, or a magic string
                    in order to skip authentication.
    :type secret: str

    :param nodepath: The path to the node.js executable
    :type nodepath: str

    :returns: The subprocess object created by the method.
    :rtype: subprocess.Popen
    """
    return _run_node(nodepath, server_fd, secret)

"""Module for starting processes"""
from six.moves import map
import os
import subprocess


def _find_mainjs():
    moduledir = os.path.split(__file__)[0]
    return os.path.join(moduledir, "js", "main.js")


def _run_node(nodepath="node", *args):
    to_call = [nodepath, _find_mainjs()]
    to_call.extend(map(str, args))
    print(to_call)
    return subprocess.Popen(to_call, bufsize=0)

def open_process(server_fd, secret, nodepath="node"):
    return _run_node(nodepath, server_fd, secret)

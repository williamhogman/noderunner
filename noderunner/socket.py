"""Module for creating socket objects"""
from __future__ import absolute_import
import gevent.socket

def get_sockets():
    # TODO: Platform checking
    return get_socket_pair()

def get_socket_pair():
    our, cli = gevent.socket.socketpair()

    return our, cli, cli.fileno()

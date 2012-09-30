"""Module for creating socket objects"""
from __future__ import absolute_import
import socket

def get_sockets():
    # TODO: Platform checking
    return get_socket_pair()

def get_socket_pair():
    our, cli = socket.socketpair()

    return our, cli, cli.fileno()

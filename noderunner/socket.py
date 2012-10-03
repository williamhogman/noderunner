"""Module for creating socket objects

This module contains function for creating the appropriate sockets
depending on the platform. On *nix this should be a socketpair, other
platforms are not yet supported.
"""

from __future__ import absolute_import
import gevent.socket


def get_sockets():
    """Gets the sockets for communication between server and client

    This function returns appropriate sockets to use for client server
    communication. The first part should be a socket or file like
    object for use by the Python portition of NodeRunner the second
    part may be a socket or file like object that the client should
    use. The third must be a FD or string that tells the Javascript
    portion where to connect to.

    :returns: A triple containing the python socket,
              the javascript socket (or None), and finally
              a FD or a string specifying where the client
              should connect.
    :rtype: 3 tuple of socket, socket or None, string or int
    """
    # TODO: Platform checking
    return get_socket_pair()


def get_socket_pair():
    """Returns a socket pair on *nix operating systems."""
    our, cli = gevent.socket.socketpair()

    return our, cli, cli.fileno()

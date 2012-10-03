from mock import patch, sentinel, Mock
from nose.tools import eq_, ok_
from noderunner.socket import get_sockets, get_socket_pair


@patch("noderunner.socket.get_socket_pair",
       return_value=(sentinel.servsock,
                     sentinel.clisock,
                     sentinel.clifd))
def test_get_sockets(p):
    serv, cli, fd = get_sockets()

    eq_(serv, sentinel.servsock)
    eq_(cli, sentinel.clisock)
    eq_(fd, sentinel.clifd)


@patch("gevent.socket.socketpair",
       return_value=(Mock(), Mock()))
def test_get_socket_pair(p):
    py, js = p.return_value
    js.fileno.return_value = sentinel.clifd

    serv, cli, fd = get_socket_pair()

    eq_(serv, py)
    eq_(cli, js)
    eq_(fd, sentinel.clifd)

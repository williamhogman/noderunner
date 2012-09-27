""" Tests for the connection module"""
import six
from mock import Mock
import io
from nose.tools import ok_, eq_, raises

from noderunner.connection import Connection

class TestConnection(object):
    _dummy_msg = six.b("\x01t\x00\x00\x00\x00\x00\r" + '"Hello World"')

    def _socket(self):
        m = Mock(name="MockSocket", spec=io.RawIOBase)
        m.closed = False
        return m

    def _with_data(self, bfr):
        s = self._socket()
        stream = six.BytesIO(bfr)
        s.read.side_effect = stream.read

        return s, stream

    def test_read_packet(self):
        s = self._socket()
        # Version = 1, type = 't', len = 31
        msg = self._dummy_msg

        s, stream = self._with_data(msg)

        c = Connection(s)

        kind, body = c.read_packet()

        eq_(kind, 116)
        eq_(body, "Hello World")
        eq_(stream.tell(), len(msg))

    @raises(RuntimeError)
    def test_wrong_version(self):
        # Just a header, just reading the invalid
        # number causes an exception.
        # Version = 99, type = 1 len= 5
        msg = six.b('c\x01\x00\x00\x00\x00\x00\x05')
        s, stream = self._with_data(msg)

        c = Connection(s)

        c.read_packet()

    def test_send_packet(self):
        stream = six.BytesIO()

        c = Connection(stream)

        c.send_packet(1, "Hello World")
        eq_(stream.getvalue(),
            six.b('\x01\x01\x00\x00\x00\x00\x00\r"Hello World"'))

    def test_packets(self):
        s, stream = self._with_data(self._dummy_msg)

        c = Connection(s)

        kind, body = six.next(c.packets())

        eq_(kind, 116)
        eq_(body, "Hello World")
        eq_(stream.tell(), len(self._dummy_msg))

    @raises(StopIteration)
    def test_no_packets(self):
        s = self._socket()
        s.closed = True
        c = Connection(s)

        six.next(c.packets())

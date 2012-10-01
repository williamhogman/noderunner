"""Tests for the protocol module"""
import threading
import time
from mock import Mock, patch, sentinel
from nose.tools import ok_, eq_, raises

from noderunner.protocol import (Protocol,
                                 ResponseManager,
                                 MSG_CHALLENGE,
                                 MSG_AUTH,
                                 MSG_AUTH_RESP,
                                 MSG_RESPONSE,
                                 MSG_REQUEST)

from noderunner.connection import Connection


class TestProtocol(object):
    _response_data = dict(response_to=1, type="json", obj="foo")

    def _connection(self, packets=[]):
        mck = Mock(spec=Connection)
        mck.packets.return_value = packets
        return mck

    def _with_pck(self, *pcks):
        con = self._connection(packets=pcks)
        return con

    def test_start(self):
        con = self._connection()

        p = Protocol(con, "foo")
        p.start()
        con.send_packet.assert_called_once_with(ord('h'), {"hello": "hello"})

    @patch("noderunner.crypto.sign_challenge", return_value=sentinel.signed)
    def test_responds_to_challenge(self, p):
        con = self._with_pck((MSG_CHALLENGE, dict(challenge="0" * 64)))
        p = Protocol(con, "foo")

        p._loop()

        con.send_packet.assert_called_once_with(
            MSG_AUTH,  dict(signature=sentinel.signed)
        )

    def test_accept_auth_resp(self):
        con = self._with_pck((MSG_AUTH_RESP, dict(status=True)))

        p = Protocol(con, "foo")

        p._loop()

        ok_(p.authenticated)

    def test_auth_resp_invalid(self):
        con = self._with_pck((MSG_AUTH_RESP, dict(status=False)))

        p = Protocol(con, "foo")
        p._loop()

        ok_(not p.authenticated)

    def test_request_sync(self):
        con = self._with_pck((MSG_RESPONSE, self._response_data))

        p = Protocol(con, "foo")
        p._authed = True

        def fn():
            time.sleep(0.001)
            p._loop()

        th = threading.Thread(target=fn)
        th.start()

        args = dict(somearg=sentinel.somearg)
        ret = p.request_sync(sentinel.mtd, timeout=1, **args)

        eq_(ret, "foo")
        con.send_packet.assert_called_once_with(MSG_REQUEST, {
            "reqid": 1,
            "action": sentinel.mtd,
            "args": args
            })
        th.join()

    def test_request_async(self):
        con = self._with_pck((MSG_RESPONSE, self._response_data))

        p = Protocol(con, "foo")
        p._authed = True

        args = dict(somearg=sentinel.somearg)
        handle = p.request(sentinel.mtd, **args)

        p._loop()

        # calling handle should wait the response
        ret = handle()

        eq_(ret, "foo")
        con.send_packet.assert_called_once_with(MSG_REQUEST, {
            "reqid": 1,
            "action": sentinel.mtd,
            "args": args
            })


class TestResponseManager(object):
    @raises(RuntimeError)
    def test_timeout(self):
        r = ResponseManager()

        r.pending(100)

        r.await(100, 0)

    def test_arrive_instant(self):
        r = ResponseManager()
        r.pending(100)
        r.arrived(100, sentinel.foo)
        ret = r.await(100)
        eq_(ret, sentinel.foo)

    def test_arrive_threaded(self):
        r = ResponseManager()
        r.pending(100)

        def fn():
            time.sleep(0)
            r.arrived(100, sentinel.foo)

        th = threading.Thread(target=fn)
        th.start()
        ret = r.await(100, 1)
        th.join(1)

        eq_(ret, sentinel.foo)

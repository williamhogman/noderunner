"""Module implementing the noderunner protocol"""
import sys
import functools
import time

import six

import gevent
import gevent.coros
import gevent.event

import noderunner.crypto
import noderunner.objects

# Initialization
MSG_HELLO = ord('h')
MSG_CHALLENGE = ord('C')
MSG_AUTH = ord('a')
MSG_AUTH_RESP = ord("A")

# Runtime
MSG_REQUEST = ord('r')
MSG_RESPONSE = ord('R')
MGS_EVENT = ord("E")


class _RequestCounter(object):
    def __init__(self, initial_value=0):
        self._val = initial_value
        self._lock = gevent.coros.Semaphore()

    def __call__(self):
        with self._lock:
            self._val += 1
            return self._val


class Protocol(object):
    def __init__(self, connection, secret):
        """Takes a connection"""
        self._connection = connection
        self._secret = secret
        self._authed = False
        self._authed_event = gevent.event.Event()
        self._dispatch = {
            MSG_CHALLENGE: self._on_challenge,
            MSG_AUTH_RESP: self._on_auth_resp,
            MSG_RESPONSE: self._on_response
        }
        self._req_counter = _RequestCounter()
        self._rmgr = ResponseManager()

    @property
    def authenticated(self):
        return self._authed

    def _launch_thread(self):
        th = gevent.Greenlet(self._loop)
        th.start()

        self._th = th

    def _loop(self):
        for method, body in self._connection.packets():
            print("python got" ,method, body)
            fn = self._dispatch.get(method, None)
            if not fn:
                raise RuntimeError("Couldn't find handler for method {0}"
                                   .format(method))
            fn(body)

    def _send(self, msgid, body):
        self._connection.send_packet(msgid, body)

    def _send_auth(self, signature):
        self._send(MSG_AUTH, dict(signature=signature))

    def _on_challenge(self, body):
        chng = body.get("challenge", None)
        if not chng or len(chng) != 2 * 32:
            raise RuntimeError("Invalid challenge")
        sign = noderunner.crypto.sign_challenge(self._secret, chng)
        self._send_auth(sign)

    def _on_auth_resp(self, body):
        status = body.get("status", False)
        self._authed = bool(status)
        if self._authed:
            self._authed_event.set()

    def _on_response(self, body):
        our_id = body["response_to"]
        msg = noderunner.objects.from_js(body["type"], body["obj"])
        self._rmgr.arrived(our_id, msg)

    def start(self):
        self._send(MSG_HELLO, dict(hello="hello"))
        self._launch_thread()

    def stop(self):
        self._connection.stop()
        self._th.join(3)
        self._connection.force_stop()

    def _send_request(self, action, reqid, args):
        data = dict(reqid=reqid, action=action, args=args)
        self._send(MSG_REQUEST, data)

        return reqid

    def _perform_request(self, action, args):
        if not self._authed:
            self._authed_event.wait()
            if not self._authed:
                raise RuntimeError("Not authenticated")

        reqid = self._req_counter()
        # Mark id as pending
        self._rmgr.pending(reqid)
        self._send_request(action, reqid, args)

        return reqid

    def request_sync(self, action, timeout=10, **kwargs):
        reqid = self._perform_request(action, kwargs)

        val = self._rmgr.await(reqid, timeout=timeout)
        return val

    def request(self, action, **kwargs):
        reqid = self._perform_request(action, kwargs)

        handle = functools.partial(self._rmgr.await, reqid)

        return handle

class ResponseManager(object):

    def __init__(self):
        self._events = dict()

    def _cleanup(self, msgid):
        if msgid in self._events:
            del self._events[msgid]

    def pending(self, msgid):
        self._events[msgid] = gevent.event.AsyncResult()

    def await(self, msgid, timeout=10):
        """Awaits a message with the passed in id"""
        try:
            return self._events[msgid].get(timeout)
        finally:
            self._cleanup(msgid)

    def arrived(self, msgid, contents):
        """Signals the arrival of a message with a given id"""
        self._events[msgid].set(contents)

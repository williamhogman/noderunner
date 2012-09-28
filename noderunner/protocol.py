"""Module implementing the noderunner protocol"""
import sys
import threading
import functools

import six

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
        self._lock = threading.Lock()

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
        self._dispatch = {
            MSG_CHALLENGE: self._on_challenge,
            MSG_AUTH_RESP: self._on_auth_resp,
            MSG_RESPONSE: self._on_response
        }
        self._req_conunter = _RequestCounter()
        self._rmgr = ResponseManager()

    @property
    def authenticated(self):
        return self._authed

    def _loop(self):
        for method, body in self._connection.packets():
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

    def _on_response(self, body):
        our_id = body["response_to"]
        msg = noderunner.objects.from_js(body["type"], body["obj"])
        self._rmgr.arrived(our_id, msg)

    def start(self):
        self._send(MSG_HELLO, dict(hello="hello"))

    def _send_request(self, action, reqid, args):
        data = dict(reqid=reqid, action=action, args=args)
        self._send(MSG_REQUEST, data)

        return reqid

    def _perform_request(self, action, args):
        if not self._authed:
            raise RuntimeError("Not authenticated")

        reqid = self._req_conunter()
        # Mark id as pending
        self._rmgr.pending(reqid)
        self._send_request(action, reqid, args)

        return reqid

    def request_sync(self, action, timeout=10, **kwargs):
        reqid = self._perform_request(action, kwargs)

        val = self._rmgr.await(reqid,timeout=timeout)
        return val

    def request(self, action, **kwargs):
        reqid = self._perform_request(action, kwargs)

        handle = functools.partial(self._rmgr.await, reqid)

        return handle

# 3.1>= and 2.7>= have an atomic wait function
if (six.PY3 and sys.version_info[1] >= 1) or (sys.version_info[1] >= 7):
    def _event_wait(event, timeout):
         if event.wait(timeout):
             return True
         else:
             raise RuntimeError("Timed out waiting for event")
else: # very unlikely to go wrong but felt better to use the correct version aboove
    def _event_wait(event, timeout):
        event.wait(timeout)
        if event.is_set():
            return True
        else:
            raise RuntimeError("Timed out waiting for event")


class ResponseManager(object):

    def __init__(self):
        self._events = dict()
        self._responses = dict()

    def _cleanup(self, msgid):
        if msgid in self._events:
            del self._events[msgid]
        if msgid in self._responses:
            del self._responses[msgid]

    def pending(self, msgid):
        self._events[msgid] = threading.Event()

    def await(self, msgid, timeout=10):
        """Awaits a message with the passed in id"""
        try:
            _event_wait(self._events[msgid], timeout)
            return self._responses[msgid]
        finally:
            self._cleanup(msgid)

    def arrived(self, msgid, contents):
        """Signals the arrival of a message with a given id"""
        self._responses[msgid] = contents
        self._events[msgid].set()

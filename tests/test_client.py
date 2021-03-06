from mock import Mock, patch, ANY, sentinel
from nose.tools import ok_, eq_, raises, timed

from noderunner.client import Client, Context, Handle
from noderunner.connection import Connection
from noderunner.protocol import Protocol

class TestClient(object):

    @patch("noderunner.client.get_sockets")
    @patch("noderunner.client.open_process")
    @patch("noderunner.client.Connection", spec=Connection)
    @patch("noderunner.client.Protocol", spec=Protocol)
    def _client(self, proto, con, proc, sock):
        sock.return_value = (Mock(), Mock(), Mock())
        return Client(), proto, con, proc, sock

    def test_ctor(self):
        c, proto, con, proc, sock = self._client()

        proto.assert_called_once_with(con.return_value, ANY)
        con.assert_called_once_with(ANY)
        proc.assert_called_once_with(ANY, ANY)
        sock.assert_called_once_with()

    def test_eval(self):
        c, proto, con, proc, sock = self._client()

        c.eval(sentinel.code, sentinel.context)

        p = proto.return_value
        p.request_sync.assert_called_once_with("eval",
                                               code=sentinel.code,
                                               context=sentinel.context)

    def test_stop(self):
        c, proto, con, proc, sock = self._client()

        c.stop()
        proc.return_value.terminate.assert_called_once_with()
        proto.return_value.stop.assert_called_once_with()

    def test_context(self):
        c, proto, con, proc, sock = self._client()

        c.context(sentinel.name, sentinel.deps)

        p = proto.return_value
        p.request_sync.assert_called_once_with("mkcontext",
                                               name=sentinel.name,
                                               requirements=sentinel.deps)

    def test_get(self):
        c, proto, con, proc, sock = self._client()

        c.get(sentinel.path, sentinel.context)

        p = proto.return_value
        p.request_sync.assert_called_once_with("get",
                                               path=sentinel.path,
                                               context=sentinel.context)

    def test_set(self):
        c, proto, con, proc, sock = self._client()

        c.set(sentinel.path, sentinel.val, sentinel.context)

        p = proto.return_value
        p.request_sync.assert_called_once_with("set",
                                               path=sentinel.path,
                                               value=sentinel.val,
                                               context=sentinel.context)

    def test_call(self):
        c, proto, con, proc, sock = self._client()

        c.call(sentinel.path, sentinel.args, sentinel.context)

        p = proto.return_value
        p.request_sync.assert_called_once_with("call",
                                               path=sentinel.path,
                                               args=sentinel.args,
                                               context=sentinel.context)


class TestContext(object):

    def _context(self, name=sentinel.name):
        mck = Mock()
        return mck, Context(mck, name)

    def test_eval(self):
        mck, context = self._context()

        context.eval(sentinel.code)

        mck.eval.assert_called_once_with(sentinel.code,
                                         context=sentinel.name)

    def test_get(self):
        mck, context = self._context()

        context.get(sentinel.path)

        mck.get.assert_called_once_with(ANY, sentinel.name)

    def test_set(self):
        mck, context = self._context()

        context.set(sentinel.path, sentinel.value)

        mck.set.assert_called_once_with(ANY,
                                        sentinel.value,
                                        sentinel.name)

    def test_call(self):
        mck, context = self._context()

        context.call(sentinel.path, sentinel.args)
        mck.call.assert_called_once_with(ANY,
                                         sentinel.args,
                                         sentinel.name)

    def test_objects(self):
        mck, context = self._context()

        handle = context.objects

        eq_(handle._context, context)


class TestHandle(object):

    def test_call(self):
        ctx = Mock()
        ctx.call.return_value = sentinel.rtn

        h = Handle(ctx)

        eq_(h(sentinel.foo), sentinel.rtn)

        ctx.call.assert_called_once_with((sentinel.foo,))

    def test_attr_access(self):
        ctx = Mock()

        h = Handle(ctx)

        handle2 = h.foobar

        eq_(handle2._path, ["foobar"])

    def test_item_access(self):
        ctx = Mock()

        h = Handle(ctx)

        handle2 = h["foobar"]

        eq_(handle2._path, ["foobar"])

    def test_access_context_stays(self):
        ctx = Mock()
        h = Handle(ctx)
        handle2 = h.foobar
        eq_(handle2._context, ctx)

    def test_get(self):
        ctx = Mock()
        ctx.get.return_value = sentinel.get

        h = Handle(ctx)

        eq_(h.get(), sentinel.get)

        ctx.get.assert_called_once_with()

    def test_attr_set(self):
        ctx = Mock()
        h = Handle(ctx)

        h.key = sentinel.val
        ctx.set.assert_called_once_with("key", sentinel.val)

    def test_item_set(self):
        ctx = Mock()
        h = Handle(ctx)

        h["key"] = sentinel.val
        ctx.set.assert_called_once_with("key", sentinel.val)

import six
from mock import Mock, sentinel
import io
from nose.tools import ok_, eq_, raises, timed, raises

from noderunner.objects import from_js, JSError, Undefined

class TestFromJS(object):

    def test_json_is_identity(self):
        ret = from_js("json", sentinel.foo)
        eq_(ret, sentinel.foo)

    def test_err(self):
        obj = dict(name=sentinel.name, message=sentinel.message)
        ret = from_js("err", obj)

        ok_(isinstance(ret, JSError))
        eq_(ret.name, sentinel.name)
        eq_(ret.message, sentinel.message)

    def test_undefined(self):
        ret = from_js("undefined", sentinel.whatever)
        eq_(ret, Undefined)

    @raises(RuntimeError)
    def test_invalid_type(self):
        from_js(sentinel.invalid_kind, {})

def test_undefined():
    eq_(bool(Undefined), False)
    eq_(str(Undefined), "undefined")
    eq_(repr(Undefined), "noderunner.objects.Undefined")

"""Module containing methods for converting JavaScript object into python objects and vice versa"""

class JSError(Exception):
    def __init__(self, name, message):
        self._name = name
        self._message = message

    def __str__(self):
        return "JsError:{0}: {1}".format(self._name, self._message)

class _Undefined():
    """Class representing undefined objects"""
    def __str__(self):
        return "undefined"

    def __repr__(self):
        return "noderunner.objects.Undefined"

Undefined = _Undefined()

def from_js(kind, obj):
    """Converts JS objects to python objects

    JSON-objects i.e. objects that can be represented in entirely in
    JSON are left untouched.
    """
    if kind == "json":
        return obj
    elif kind == "err":
        return JSError(obj.get("name"), obj.get("message"))
    elif kind == "undefined":
        # Undefined !== null in javascript,
        # In python we have to go with this solution
        return Undefined


    raise RuntimeError("Unknown js object kind {0}".format(kind))

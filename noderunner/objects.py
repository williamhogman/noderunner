"""Module containing methods for converting JavaScript object into python objects and vice versa"""

def from_js(kind, obj):
    """Converts JS objects to python objects

    JSON-objects i.e. objects that can be represented in entirely in
    JSON are left untouched.
    """
    if kind == "json":
        return obj

    raise RuntimeError("Unknown js object kind {0}".format(kind))

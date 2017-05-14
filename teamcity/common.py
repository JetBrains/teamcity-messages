# coding=utf-8

import sys
import traceback
import inspect


_max_reported_output_size = 1 * 1024 * 1024
_reported_output_chunk_size = 50000

PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode  # noqa: F821
    binary_type = str
else:
    text_type = str
    binary_type = bytes

_sys_stdout_encoding = sys.stdout.encoding


def limit_output(data):
    return data[:_max_reported_output_size]


def split_output(data):
    while len(data) > 0:
        if len(data) <= _reported_output_chunk_size:
            yield data
            data = ''
        else:
            yield data[:_reported_output_chunk_size]
            data = data[_reported_output_chunk_size:]


def is_string(obj):
    if sys.version_info >= (3, 0):
        return isinstance(obj, str)
    else:
        return isinstance(obj, basestring)  # noqa: F821


def get_output_encoding():
    import locale
    loc = locale.getdefaultlocale()
    if loc[1]:
        return loc[1]
    return _sys_stdout_encoding


def get_exception_message(e):
    if e.args and isinstance(e.args[0], binary_type):
        return e.args[0].decode(get_output_encoding())
    return text_type(e)


def to_unicode(obj):
    if isinstance(obj, binary_type):
        return obj.decode(get_output_encoding())
    elif isinstance(obj, text_type):
        return obj
    else:
        if PY2:
            raise TypeError("Expected str or unicode")
        else:
            raise TypeError("Expected bytes or str")


def get_class_fullname(something):
    if inspect.isclass(something):
        cls = something
    else:
        cls = something.__class__

    module = cls.__module__
    if module is None or module == str.__class__.__module__:
        return cls.__name__
    return module + '.' + cls.__name__


def convert_error_to_string(err):
    try:
        exctype, value, tb = err
        return ''.join(traceback.format_exception(exctype, value, tb))
    except:
        tb = traceback.format_exc()
        return "*FAILED TO GET TRACEBACK*: " + tb

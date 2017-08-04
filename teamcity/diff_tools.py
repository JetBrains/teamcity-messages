import base64
import pprint
import sys
import unittest

_PY2K = sys.version_info < (3,)


def patch_unittest_diff():
    """
    Patches "assertEquals" to throw DiffError
    """
    def _patched_equals(_, first, second, msg=None):
        if first != second:
            raise DiffError(first, second, msg)

    unittest.TestCase.assertEqual = _patched_equals


def _format_and_convert(string):
    string = pprint.pformat(string)
    return string if _PY2K else bytes(str(string), "utf-8")


class DiffError(AssertionError):

    def __init__(self, expected, actual, msg=None, preformated=False):
        super(AssertionError, self).__init__()
        self.expected = expected
        self.actual = actual
        self.msg = msg

        if preformated:
            return
        self.expected = pprint.pformat(self.expected)
        self.actual = pprint.pformat(self.actual)
        self.msg = msg if msg else ""

    def __str__(self):
        return self._serialize()

    def __unicode__(self):
        return self._serialize()

    def _serialize(self):
        def fix_type(msg):
            return msg if _PY2K else bytes(str(msg), "utf-8")

        encoded_fields = [base64.b64encode(fix_type(x)) for x in [self.expected, self.actual, self.msg]]
        if not _PY2K:
            encoded_fields = [bytes.decode(x) for x in encoded_fields]
        return "|".join(encoded_fields)


def deserialize_error(serialized_message):
    parts = [base64.b64decode(x) for x in str(serialized_message).split("|")]
    if not _PY2K:
        parts = [bytes.decode(x) for x in parts]
    return DiffError(parts[0], parts[1], parts[2], preformated=True)

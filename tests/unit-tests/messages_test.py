from teamcity.messages import TeamcityServiceMessages
from datetime import datetime
import os
import sys
import tempfile
import textwrap


class StreamStub(object):
    def __init__(self):
        self.observed_output = ''

    def write(self, msg):
        self.observed_output += msg

    def flush(self):
        pass

fixed_date = datetime(2000, 11, 2, 10, 23, 1, 556789)


def test_no_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556']\n"


def test_one_property():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage', fruit='apple')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556' fruit='apple']\n"


def test_three_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage', fruit='apple', meat='steak', pie='raspberry')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556' fruit='apple' meat='steak' pie='raspberry']\n"


def test_unicode():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    bjork = u'Bj\xf6rk Gu\xf0mundsd\xf3ttir'
    messages.message(bjork)
    assert stream.observed_output == "\n##teamcity[%s timestamp='2000-11-02T10:23:01.556']\n" % bjork.encode('utf-8')


def test_unicode_to_sys_stdout_with_no_encoding():
    with tempfile.NamedTemporaryFile() as tmpf:
        tmpf.write(textwrap.dedent(r"""
            from teamcity.messages import TeamcityServiceMessages

            bjork = u'Bj\xf6rk Gu\xf0mundsd\xf3ttir'

            messages = TeamcityServiceMessages()
            messages.message(bjork)
            print("hello")
            """))
        tmpf.flush()

        ret = os.system("%s %s" % (sys.executable, tmpf.name))
        assert ret == 0

        # If we don't encode output, we could run into an error like this:
        #
        # Traceback (most recent call last):
        #   File "/var/folders/gw/w0clrs515zx9x_55zgtpv4mm0000gp/T/tmp5eApc3", line 7, in <module>
        #     messages.message(bjork)
        #   File "/Users/marca/dev/git-repos/teamcity-python/teamcity/messages.py", line 30, in message
        #     self.output.write(message)
        # UnicodeEncodeError: 'ascii' codec can't encode character u'\xf6' in position 14: ordinal not in range(128)

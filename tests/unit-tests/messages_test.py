from teamcity.messages import TeamcityServiceMessages
from datetime import datetime
import os
import sys
import tempfile
import textwrap
import subprocess


if sys.version_info < (3, ):
    # Python 2
    def b(s):
        return s
else:
    # Python 3
    def b(s):
        return s.encode('latin-1')


class StreamStub(object):
    def __init__(self):
        self.observed_output = ''.encode('utf-8')

    def write(self, msg):
        self.observed_output += msg

    def flush(self):
        pass

fixed_date = datetime(2000, 11, 2, 10, 23, 1, 556789)


def test_no_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556']\n".encode('utf-8')


def test_one_property():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage', fruit='apple')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556' fruit='apple']\n".encode('utf-8')


def test_three_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage', fruit='apple', meat='steak', pie='raspberry')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556' fruit='apple' meat='steak' pie='raspberry']\n".encode('utf-8')


def test_unicode():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    if sys.version_info < (3, ):
        bjork = 'Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir'.decode('utf-8')
    else:
        bjork = b('Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir').decode('utf-8')
    messages.message(bjork)
    assert stream.observed_output == ("\n##teamcity[%s timestamp='2000-11-02T10:23:01.556']\n" % bjork).encode('utf-8')


def test_unicode_to_sys_stdout_with_no_encoding():
    tempdir = tempfile.mkdtemp()
    file_name = os.path.join(tempdir, "testfile.py")
    try:
        f = open(file_name, "wb")
        f.write((textwrap.dedent(r"""
            import sys
            sys.path = %s

            from teamcity.messages import TeamcityServiceMessages

            if sys.version_info < (3, ):
                # Python 2
                def b(s):
                    return s
            else:
                # Python 3
                def b(s):
                    return s.encode('latin-1')

            bjork = b('Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir').decode('utf-8')

            messages = TeamcityServiceMessages(encoding='utf-8')
            messages.message(bjork)
            """) % sys.path).encode('utf-8'))
        f.close()

        ret = subprocess.call([sys.executable, file_name])
        assert ret == 0
    finally:
        os.unlink(file_name)
        os.rmdir(tempdir)

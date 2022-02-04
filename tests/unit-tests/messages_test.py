from teamcity.messages import TeamcityServiceMessages, escape_value

from datetime import datetime
import errno
import io
import os
import sys
import time
import tempfile
import textwrap
import subprocess
import unicodedata

import pytest


_PY2 = sys.version_info < (3, )


if _PY2:
    # Python 2
    def b(s):
        return s
else:
    # Python 3
    def b(s):
        return s.encode('latin-1')


class StreamStub(object):
    def __init__(self, raise_ioerror=None):
        self.observed_output = ''.encode('utf-8')
        self.raise_ioerror = raise_ioerror

    def write(self, msg):
        if self.raise_ioerror:
            # Raise the first time it's called, but not the second
            errno = self.raise_ioerror
            self.raise_ioerror = None
            raise IOError(errno, 'io error!')
        self.observed_output += msg

    def flush(self):
        pass


fixed_date = time.mktime(datetime(2000, 11, 2, 10, 23, 1).timetuple()) + 0.5569


def test_escape_value():
    assert escape_value("[square brackets]") == "|[square brackets|]"
    assert escape_value("(parentheses)") == "(parentheses)"
    assert escape_value("'single quotes'") == "|'single quotes|'"
    assert escape_value("|vertical bars|") == "||vertical bars||"
    assert escape_value("line1\nline2\nline3") == "line1|nline2|nline3"


def test_publish_artifacts():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.publishArtifacts('/path/to/file')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[publishArtifacts '/path/to/file']
        """).strip().encode('utf-8')


def test_progress_message():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.progressMessage('doing stuff')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[progressMessage 'doing stuff']
        """).strip().encode('utf-8')


def test_progress_message_unicode():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    if _PY2:
        bjork = 'Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir'.decode('utf-8')
    else:
        bjork = b('Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir').decode('utf-8')
    messages.progressMessage(bjork)
    expected_output = b(
        "##teamcity[progressMessage "
        "'Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir']")
    assert stream.observed_output.strip() == expected_output


def test_message_unicode():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    if sys.version_info < (3, ):
        bjork = 'Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir'.decode('utf-8')
    else:
        bjork = b('Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir').decode('utf-8')
    messages.message('foo', u=bjork, b=bjork.encode('utf-8'))
    expected_output = b(
        "##teamcity[foo timestamp='2000-11-02T10:23:01.556' "
        "b='Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir' "
        "u='Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir']")
    assert stream.observed_output.strip() == expected_output


def test_block_opened():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.blockOpened('dummyMessage')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[blockOpened timestamp='2000-11-02T10:23:01.556' name='dummyMessage']
        """).strip().encode('utf-8')


def test_block_closed():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.blockClosed('dummyMessage')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[blockClosed timestamp='2000-11-02T10:23:01.556' name='dummyMessage']
        """).strip().encode('utf-8')


def test_compilation_started():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.compilationStarted('gcc')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[compilationStarted timestamp='2000-11-02T10:23:01.556' compiler='gcc']
        """).strip().encode('utf-8')


def test_compilation_finished():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.compilationFinished('gcc')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[compilationFinished timestamp='2000-11-02T10:23:01.556' compiler='gcc']
        """).strip().encode('utf-8')


def test_test_suite_started():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testSuiteStarted('suite emotion')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testSuiteStarted timestamp='2000-11-02T10:23:01.556' name='suite emotion']
        """).strip().encode('utf-8')


def test_test_suite_finished():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testSuiteFinished('suite emotion')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testSuiteFinished timestamp='2000-11-02T10:23:01.556' name='suite emotion']
        """).strip().encode('utf-8')


def test_test_started():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testStarted('only a test')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testStarted timestamp='2000-11-02T10:23:01.556' name='only a test']
        """).strip().encode('utf-8')


def test_test_finished():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testFinished('only a test')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testFinished timestamp='2000-11-02T10:23:01.556' name='only a test']
        """).strip().encode('utf-8')


def test_test_ignored():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testIgnored(testName='only a test', message='some message')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testIgnored timestamp='2000-11-02T10:23:01.556' message='some message' name='only a test']
        """).strip().encode('utf-8')


def test_test_failed():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testFailed(testName='only a test', message='some message', details='details')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testFailed timestamp='2000-11-02T10:23:01.556' details='details' message='some message' name='only a test']
        """).strip().encode('utf-8')


def test_test_stdout():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testStdOut(testName='only a test', out='out')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testStdOut timestamp='2000-11-02T10:23:01.556' name='only a test' out='out']
        """).strip().encode('utf-8')


def test_test_stderr():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.testStdErr(testName='only a test', out='out')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testStdErr timestamp='2000-11-02T10:23:01.556' name='only a test' out='out']
        """).strip().encode('utf-8')


def test_progress_start():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.progressStart('doing stuff')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[progressStart 'doing stuff']
        """).strip().encode('utf-8')


def test_progress_finish():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.progressFinish('doing stuff')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[progressFinish 'doing stuff']
        """).strip().encode('utf-8')


def test_build_problem():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.buildProblem(description='something is wrong', identity='me')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[buildProblem timestamp='2000-11-02T10:23:01.556' description='something is wrong' identity='me']
        """).strip().encode('utf-8')


def test_build_status():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.buildStatus(status='failure', text='compile error')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[buildStatus timestamp='2000-11-02T10:23:01.556' status='failure' text='compile error']
        """).strip().encode('utf-8')


def test_set_parameter():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.setParameter(name='env', value='mt3')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[setParameter timestamp='2000-11-02T10:23:01.556' name='env' value='mt3']
        """).strip().encode('utf-8')


def test_build_statistic_lines_covered():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.buildStatisticLinesCovered(495)
    assert stream.observed_output.strip() == textwrap.dedent("""\
            ##teamcity[buildStatisticValue timestamp='2000-11-02T10:23:01.556' key='CodeCoverageAbsLCovered' value='495']
        """).strip().encode('utf-8')


def test_build_statistic_total_lines():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.buildStatisticTotalLines(495)
    assert stream.observed_output.strip() == textwrap.dedent("""\
            ##teamcity[buildStatisticValue timestamp='2000-11-02T10:23:01.556' key='CodeCoverageAbsLTotal' value='495']
        """).strip().encode('utf-8')


def test_build_statistic_lines_uncovered():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.buildStatisticLinesUncovered(5)
    assert stream.observed_output.strip() == textwrap.dedent("""\
            ##teamcity[buildStatisticValue timestamp='2000-11-02T10:23:01.556' key='CodeCoverageAbsLUncovered' value='5']
        """).strip().encode('utf-8')


def test_enable_service_messages():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.enableServiceMessages()
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[enableServiceMessages timestamp='2000-11-02T10:23:01.556']
        """).strip().encode('utf-8')


def test_disable_service_messages():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.disableServiceMessages()
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[disableServiceMessages timestamp='2000-11-02T10:23:01.556']
        """).strip().encode('utf-8')


def test_import_data():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.importData('junit', '/path/to/junit.xml')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[importData timestamp='2000-11-02T10:23:01.556' path='/path/to/junit.xml' type='junit']
        """).strip().encode('utf-8')


def test_custom_message():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.customMessage('blah blah blah', status='all good')
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[message timestamp='2000-11-02T10:23:01.556' errorDetails='' status='all good' text='blah blah blah']
        """).strip().encode('utf-8')


def test_no_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage')
    assert stream.observed_output == "##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556']\n".encode('utf-8')


def test_one_property():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage', fruit='apple')
    assert stream.observed_output == "##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556' fruit='apple']\n".encode('utf-8')


def test_three_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    messages.message('dummyMessage', fruit='apple', meat='steak', pie='raspberry')
    assert stream.observed_output == "##teamcity[dummyMessage timestamp='2000-11-02T10:23:01.556' fruit='apple' meat='steak' pie='raspberry']\n".encode('utf-8')


def test_unicode():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    if _PY2:
        bjork = 'Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir'.decode('utf-8')
    else:
        bjork = b('Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir').decode('utf-8')
    messages.message(bjork)
    assert stream.observed_output == ("##teamcity[%s timestamp='2000-11-02T10:23:01.556']\n" % bjork).encode('utf-8')


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


def test_handling_eagain_ioerror():
    stream = StreamStub(raise_ioerror=errno.EAGAIN)
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    assert stream.raise_ioerror == errno.EAGAIN
    messages.testStarted('only a test')
    assert stream.raise_ioerror is None
    assert stream.observed_output == b(
        '##teamcity['
        'testStarted'
        ' timestamp=\'2000-11-02T10:23:01.556\''
        ' name=\'only a test\''
        ']\n'
    )


class CustomEncodingStream(object):
    def __init__(self, encoding):
        self._buffer = io.BytesIO()
        self._encoding = encoding
        self._stream = io.TextIOWrapper(self._buffer, encoding=self._encoding, newline='\n')

    @property
    def encoding(self):
        return self._encoding

    def write(self, msg):
        if _PY2 and isinstance(msg, str):
            msg = msg.decode(self.encoding)
        self._stream.write(msg)

    def flush(self):
        self._stream.flush()

    def getvalue(self):
        return self._buffer.getvalue().decode(self.encoding)

    if not _PY2:
        @property
        def buffer(self):
            return self._buffer


@pytest.mark.parametrize(('encoding', 'is_message_encodable'),
                         [('cp1251', True), ('cp1252', False)])
def test_mismatched_encoding(encoding, is_message_encodable):
    stream = CustomEncodingStream(encoding)
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    value = unicodedata.lookup('CYRILLIC CAPITAL LETTER IO')
    messages.message(value)

    if is_message_encodable:
        expected_value = value
    else:
        expected_value = value.encode('unicode-escape').decode('latin-1')

    assert stream.getvalue() == "##teamcity[%s timestamp='2000-11-02T10:23:01.556']\n" % expected_value

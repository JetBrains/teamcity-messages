from teamcity.messages import TeamcityServiceMessages
from datetime import datetime
import textwrap


class StreamStub(object):
    def __init__(self):
        self.observed_output = ''.encode('utf-8')

    def write(self, msg):
        self.observed_output += msg

    def flush(self):
        pass


fixed_date = datetime(2000, 11, 2, 10, 23, 1, 556789)


def test_blocks():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.block("Doing something that's important"):
        messages.message("Doing stuff")
    expected_output = textwrap.dedent("""\
        ##teamcity[blockOpened timestamp='2000-11-02T10:23:01.556' name='Doing something that|'s important']
        ##teamcity[Doing stuff timestamp='2000-11-02T10:23:01.556']
        ##teamcity[blockClosed timestamp='2000-11-02T10:23:01.556' name='Doing something that|'s important']
        """)
    expected_output = expected_output.encode('utf-8')
    assert stream.observed_output == expected_output


def test_blocks_with_flowid():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.block("Doing something that's important", flowId='a'):
        messages.message("Doing stuff")
    expected_output = textwrap.dedent("""\
        ##teamcity[blockOpened timestamp='2000-11-02T10:23:01.556' flowId='a' name='Doing something that|'s important']
        ##teamcity[Doing stuff timestamp='2000-11-02T10:23:01.556']
        ##teamcity[blockClosed timestamp='2000-11-02T10:23:01.556' flowId='a' name='Doing something that|'s important']
        """)
    expected_output = expected_output.encode('utf-8')
    assert stream.observed_output == expected_output


def test_compilation():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.compilation('gcc'):
        pass
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[compilationStarted timestamp='2000-11-02T10:23:01.556' compiler='gcc']
        ##teamcity[compilationFinished timestamp='2000-11-02T10:23:01.556' compiler='gcc']
        """).strip().encode('utf-8')


def test_test_suite():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.testSuite('suite emotion'):
        pass
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testSuiteStarted timestamp='2000-11-02T10:23:01.556' name='suite emotion']
        ##teamcity[testSuiteFinished timestamp='2000-11-02T10:23:01.556' name='suite emotion']
        """).strip().encode('utf-8')


def test_test():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.test('only a test'):
        pass
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[testStarted timestamp='2000-11-02T10:23:01.556' name='only a test']
        ##teamcity[testFinished timestamp='2000-11-02T10:23:01.556' name='only a test']
        """).strip().encode('utf-8')


def test_progress():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.progress('only a test'):
        pass
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[progressStart 'only a test']
        ##teamcity[progressFinish 'only a test']
        """).strip().encode('utf-8')


def test_service_messages_disabled():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.serviceMessagesDisabled():
        pass
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[disableServiceMessages timestamp='2000-11-02T10:23:01.556']
        ##teamcity[enableServiceMessages timestamp='2000-11-02T10:23:01.556']
        """).strip().encode('utf-8')


def test_service_messages_enabled():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: fixed_date)
    with messages.serviceMessagesEnabled():
        pass
    assert stream.observed_output.strip() == textwrap.dedent("""\
        ##teamcity[enableServiceMessages timestamp='2000-11-02T10:23:01.556']
        ##teamcity[disableServiceMessages timestamp='2000-11-02T10:23:01.556']
        """).strip().encode('utf-8')

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
    expected_output = textwrap.dedent("""
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
    expected_output = textwrap.dedent("""
        ##teamcity[blockOpened timestamp='2000-11-02T10:23:01.556' flowId='a' name='Doing something that|'s important']

        ##teamcity[Doing stuff timestamp='2000-11-02T10:23:01.556']

        ##teamcity[blockClosed timestamp='2000-11-02T10:23:01.556' flowId='a' name='Doing something that|'s important']
        """)
    expected_output = expected_output.encode('utf-8')
    assert stream.observed_output == expected_output

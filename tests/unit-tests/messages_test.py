from teamcity.messages import TeamcityServiceMessages
from datetime import datetime


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

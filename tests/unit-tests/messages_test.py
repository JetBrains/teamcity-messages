from teamcity.messages import TeamcityServiceMessages
from datetime import datetime


class StreamStub(object):
    def __init__(self):
        self.observed_output = ''

    def write(self, msg):
        self.observed_output += msg


def test_no_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: datetime.min)
    messages.message('dummyMessage')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00']\n"


def test_one_property():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: datetime.min)
    messages.message('dummyMessage', fruit='apple')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00' fruit='apple']\n"


def test_three_properties():
    stream = StreamStub()
    messages = TeamcityServiceMessages(output=stream, now=lambda: datetime.min)
    messages.message('dummyMessage', fruit='apple', meat='steak', pie='raspberry')
    assert stream.observed_output == "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00' fruit='apple' meat='steak' pie='raspberry']\n"

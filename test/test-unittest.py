# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner
from teamcity.messages import TeamcityServiceMessages
import unittest
from datetime import datetime


class TestTeamcityMessages(unittest.TestCase):
    def testPass(self):
        assert 1 == 1

    def testAssertEqual(self):
        self.assertEqual("1", "2")

    def testAssertEqualMsg(self):
        self.assertEqual("1", "2", "message")

    def testAssert(self):
        self.assert_(False)

    def testFail(self):
        self.fail("failed")

    def testException(self):
        raise Exception("some exception")


class StreamStub(object):
    def __init__(self):
        self.observed_output = ''

    def write(self, msg):
        self.observed_output += msg


class TestMessages(unittest.TestCase):
    def test_no_properties(self):
        stream = StreamStub()
        messages = TeamcityServiceMessages(output=stream,
                                           now=lambda: datetime.min)
        messages.message('dummyMessage')
        assert stream.observed_output == \
            "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00']\n"

    def test_one_property(self):
        stream = StreamStub()
        messages = TeamcityServiceMessages(output=stream,
                                           now=lambda: datetime.min)
        messages.message('dummyMessage', fruit='apple')
        assert stream.observed_output == "\n##teamcity[dummyMessage " + \
            "timestamp='0001-01-01T00:00' fruit='apple']\n"

    def test_three_properties(self):
        stream = StreamStub()
        messages = TeamcityServiceMessages(output=stream,
                                           now=lambda: datetime.min)
        messages.message('dummyMessage', fruit='apple', meat='steak',
                         pie='raspberry')
        assert stream.observed_output == "\n##teamcity[dummyMessage " + \
            "timestamp='0001-01-01T00:00' fruit='apple' meat='steak' " + \
            "pie='raspberry']\n"


if __name__ == '__main__':
    unittest.main(testRunner=TeamcityTestRunner())

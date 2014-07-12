# coding=utf-8
from __future__ import absolute_import

from teamcity.unittestpy import TeamcityTestRunner
import unittest


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


if __name__ == '__main__':
    unittest.main(testRunner=TeamcityTestRunner())

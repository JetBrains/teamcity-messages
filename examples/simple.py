# coding=utf-8
from teamcity import is_running_under_teamcity
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
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)

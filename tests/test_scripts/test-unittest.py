# coding=utf-8
from __future__ import absolute_import
import sys

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
        self.assertTrue(False)

    def testFail(self):
        self.fail("failed")

    def testException(self):
        raise Exception("some exception")

    if sys.version_info >= (2, 7):
        # test skipping and expectedFailure markup is only available since python 2.7
        # http://docs.python.org/2/library/unittest.html#skipping-tests-and-expected-failures
        @unittest.skip("Reason for skipping")
        def testSkipped(self):
            self.fail("This should not appear")

        @unittest.expectedFailure
        def testExpectedFailure(self):
            self.fail("This is actually expected to fail")

        @unittest.expectedFailure
        def testUnexpectedSuccess(self):
            assert 1 == 1

    if sys.version_info >= (3, 4):
        # subtests are only available since python 3.4
        # https://docs.python.org/3/library/unittest.html#distinguishing-test-iterations-using-subtests
        def testSubtestSuccess(self):
            for i in range(0, 2):
                with self.subTest(i=i):
                    self.assertEqual(i, i)

        def testSubtestFailure(self):
            for i in range(0, 3):
                with self.subTest(i=i):
                    assert i % 2 == 0

if __name__ == '__main__':
    unittest.main(testRunner=TeamcityTestRunner())

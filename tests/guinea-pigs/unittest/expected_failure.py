# coding=utf-8
import sys
from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (2, 7):
    from unittest2 import main, TestCase, expectedFailure
else:
    from unittest import main, TestCase, expectedFailure


class TestSkip(TestCase):
    def test_expected_failure(self):
        self.fail("this should happen unfortunately")
    test_expected_failure = expectedFailure(test_expected_failure)

main(testRunner=TeamcityTestRunner)

# coding=utf-8
import sys
from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (2, 7):
    from unittest2 import main, TestCase, expectedFailure
else:
    from unittest import main, TestCase, expectedFailure


class TestSkip(TestCase):
    def test_unexpected_success(self):
        pass
    test_unexpected_success = expectedFailure(test_unexpected_success)

main(testRunner=TeamcityTestRunner)

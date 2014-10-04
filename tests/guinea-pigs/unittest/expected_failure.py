# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner

import unittest


class TestSkip(unittest.TestCase):
    @unittest.expectedFailure
    def test_expected_failure(self):
        self.fail("this should happen unfortunately")

unittest.main(testRunner=TeamcityTestRunner())

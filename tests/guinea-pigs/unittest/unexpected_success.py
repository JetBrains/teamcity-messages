# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner

import unittest


class TestSkip(unittest.TestCase):
    @unittest.expectedFailure
    def test_unexpected_success(self):
        pass

unittest.main(testRunner=TeamcityTestRunner())

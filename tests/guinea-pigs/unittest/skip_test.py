# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner

import unittest


class TestSkip(unittest.TestCase):
    @unittest.skip("testing skipping")
    def test_skip_me(self):
        self.fail("shouldn't happen")


unittest.main(testRunner=TeamcityTestRunner())

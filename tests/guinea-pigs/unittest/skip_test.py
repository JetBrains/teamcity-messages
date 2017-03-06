# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner
import sys
import unittest

if sys.version_info < (2, 7):
    from unittest2 import skip, main
else:
    from unittest import skip, main


class TestSkip(unittest.TestCase):
    @skip("testing skipping")
    def test_skip_me(self):
        self.fail("shouldn't happen")

    def test_ok(self):
        pass


main(testRunner=TeamcityTestRunner())

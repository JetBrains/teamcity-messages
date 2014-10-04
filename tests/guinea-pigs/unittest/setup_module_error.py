# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner

import unittest


class TestSkip(unittest.TestCase):
    def test_ok(self):
        pass


def setUpModule():
    assert 1 == 0

unittest.main(testRunner=TeamcityTestRunner())

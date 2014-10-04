# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner

import unittest


class TestXXX(unittest.TestCase):
    def test_ok(self):
        pass


def tearDownModule():
    assert 1 == 0

unittest.main(testRunner=TeamcityTestRunner())

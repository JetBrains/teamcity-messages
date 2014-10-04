# coding=utf-8
from teamcity.unittestpy import TeamcityTestRunner

import unittest


class TestXXX(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        raise RuntimeError("RRR")

    def test_ok(self):
        pass

unittest.main(testRunner=TeamcityTestRunner())

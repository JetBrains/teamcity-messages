import unittest
from unittest import TestCase

from teamcity.unittestpy import TeamcityTestRunner


class FooTest(TestCase):
    def test_1_test(self):
        pass

    def test_2_test(self):
        self.fail()

    def test_3_test(self):
        pass

unittest.main(testRunner=TeamcityTestRunner, failfast=True)

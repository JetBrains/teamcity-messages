import unittest

from teamcity.unittestpy import TeamcityTestRunner


from unittest import TestCase


class TestXXX(TestCase):
    def testSubtestSkip(self):
        for i in range(0, 3):
            with self.subTest(i=i):
                if i == 2:
                    self.skipTest("skip reason")

unittest.main(testRunner=TeamcityTestRunner)

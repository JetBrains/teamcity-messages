import sys
from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (3, 4):
    from unittest2 import main, TestCase
else:
    from unittest import main, TestCase


class TestXXX(TestCase):
    def testSubtestSkip(self):
        for i in range(0, 3):
            with self.subTest(i=i):
                if i == 2:
                    self.skipTest("skip reason")

main(testRunner=TeamcityTestRunner)

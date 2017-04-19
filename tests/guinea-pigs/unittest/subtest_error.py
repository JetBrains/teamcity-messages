import sys
from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (3, 4):
    from unittest2 import main, TestCase
else:
    from unittest import main, TestCase


class TestXXX(TestCase):
    def testSubtestError(self):
        with self.subTest(i=0):
            pass

        with self.subTest(i="abc.xxx"):
            raise RuntimeError("RRR")

main(testRunner=TeamcityTestRunner)

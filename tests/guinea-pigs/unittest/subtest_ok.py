import sys
from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (3, 4):
    from unittest2 import main, TestCase
else:
    from unittest import main, TestCase


class TestXXX(TestCase):
    def testSubtestSuccess(self):
        for i in range(0, 2):
            with self.subTest(i=i):
                self.assertEqual(i, i)

main(testRunner=TeamcityTestRunner)

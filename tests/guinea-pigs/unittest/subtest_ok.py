import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def testSubtestSuccess(self):
        for i in range(0, 2):
            with self.subTest(i=i):
                self.assertEqual(i, i)

unittest.main(testRunner=TeamcityTestRunner)

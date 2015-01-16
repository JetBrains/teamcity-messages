import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def testSubtestError(self):
        with self.subTest(i=0):
            pass

        with self.subTest(i="abc.xxx"):
            raise RuntimeError("RRR")

unittest.main(testRunner=TeamcityTestRunner)

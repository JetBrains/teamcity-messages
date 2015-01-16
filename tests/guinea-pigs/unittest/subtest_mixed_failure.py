import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def testSubtestFailure(self):
        with self.subTest(i=0):
            pass

        with self.subTest(i="abc.xxx"):
            assert 1 == 0

        assert 6 == 1

unittest.main(testRunner=TeamcityTestRunner)

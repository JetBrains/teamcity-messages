import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def testNested(self):
        with self.subTest(i=1):
            with self.subTest(i=2):
                pass

unittest.main(testRunner=TeamcityTestRunner)

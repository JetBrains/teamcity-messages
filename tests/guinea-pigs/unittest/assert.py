import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def runTest(self):
        assert 1 == 0


TeamcityTestRunner().run(TestXXX())

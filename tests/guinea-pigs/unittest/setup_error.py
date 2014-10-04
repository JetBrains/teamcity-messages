import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def setUp(self):
        raise RuntimeError("RRR")

    def runTest(self):
        assert 1 == 1


TeamcityTestRunner().run(TestXXX())

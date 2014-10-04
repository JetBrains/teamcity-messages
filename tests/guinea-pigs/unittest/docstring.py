import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def runTest(self):
        """ A test """
        assert 1 == 1


TeamcityTestRunner().run(TestXXX())

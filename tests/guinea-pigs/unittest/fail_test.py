import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestXXX(unittest.TestCase):
    def runTest(self):
        self.fail("Grr")


TeamcityTestRunner().run(TestXXX())

import unittest

from teamcity.unittestpy import TeamcityTestRunner


class TestKeyboardInterrupt(unittest.TestCase):
    def runTest(self):
        raise KeyboardInterrupt()


TeamcityTestRunner().run(TestKeyboardInterrupt())

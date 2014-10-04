import unittest

from teamcity.unittestpy import TeamcityTestRunner
from teamcity import is_running_under_teamcity


class TestXXX(unittest.TestCase):
    def runTest(self):
        assert 1 == 1


if __name__ == '__main__':
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()

    nested_suite = unittest.TestSuite()
    nested_suite.addTest(TestXXX())

    suite = unittest.TestSuite()
    suite.addTest(nested_suite)

    runner.run(suite)

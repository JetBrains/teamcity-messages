from simple_tests import SimpleTests
from nose.loader import TestLoader
from teamcity.unittestpy import TeamcityTestRunner


if __name__ == '__main__':
    test_loader = TestLoader().loadTestsFromTestClass(SimpleTests)
    TeamcityTestRunner().run(test_loader)


import os
import unittest

from teamcity.unittestpy import TeamcityTestRunner

all_tests = unittest.TestLoader().discover(os.path.join('tests', 'guinea-pigs', 'unittest', 'discovery_errors'))
TeamcityTestRunner().run(all_tests)

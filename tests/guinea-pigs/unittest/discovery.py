import os
import unittest

from teamcity.unittestpy import TeamcityTestRunner

all_tests = unittest.TestLoader().discover(os.path.join('tests', 'guinea-pigs', 'unittest', 'discovery'))
TeamcityTestRunner().run(all_tests)

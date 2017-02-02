# coding=utf-8
import sys

from teamcity.unittestpy import TeamcityTestRunner

from unittest import TestCase, main


class SpamTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print("1")

    def test_test(self):
        print("stdout_test")
        sys.stderr.write("stderr_test")

    @classmethod
    def tearDownClass(cls):
        print("3")

main(testRunner=TeamcityTestRunner(buffer=True))

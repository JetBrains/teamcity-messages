# coding=utf-8
import sys

from teamcity.unittestpy import TeamcityTestRunner

from unittest import TestCase, main


class SpamTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print("1")

    def test_test(self):
        print("stdout_test1")
        print("stdout_test2")
        sys.stderr.write("stderr_")
        sys.stderr.write("test1")
        sys.stderr.flush()

        sys.stderr.write("stderr_test2")
        raise Exception("A")

    @classmethod
    def tearDownClass(cls):
        print("3")

main(testRunner=TeamcityTestRunner(buffer=True))

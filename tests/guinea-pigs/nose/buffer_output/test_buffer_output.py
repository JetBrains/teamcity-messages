# coding=utf-8
import sys

from unittest import TestCase


class SpamTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print("1")

    def test_test(self):
        print("stdout_line1")
        print("stdout_line2")
        sys.stdout.write("stdout_line3_nonewline")
        raise Exception("A")

    @classmethod
    def tearDownClass(cls):
        print("3")

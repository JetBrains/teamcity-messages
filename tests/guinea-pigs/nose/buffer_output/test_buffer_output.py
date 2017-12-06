# coding=utf-8
import sys
import logging

from unittest import TestCase


class SpamTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print("1")

    def test_test(self):
        print("stdout_line1")
        print("stdout_line2")
        logging.getLogger("LOGGER_NAME").info("log info message")
        sys.stdout.write("stdout_line3_nonewline")
        raise Exception("A")

    @classmethod
    def tearDownClass(cls):
        print("3")

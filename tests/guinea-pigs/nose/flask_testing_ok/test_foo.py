from flask import Flask
from flask_testing import TestCase


class TestFoo(TestCase):

    def create_app(self):
        return Flask(__name__)

    def test_add(self):
        self.assertEqual(1 + 2, 3)

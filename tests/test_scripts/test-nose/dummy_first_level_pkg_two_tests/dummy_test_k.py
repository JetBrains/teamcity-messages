import unittest

import EvilClassThatDoesNotExist


class DummyTestK(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True, 'example assertion')
import unittest


class DummyTestI(unittest.TestCase):
    def test_something(self):
        evil_non_existent_method_123I()

        self.assertTrue(True, 'example assertion')

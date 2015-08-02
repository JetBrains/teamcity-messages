from twisted.trial import unittest


class CalculationTestCase(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(11, 11)

    def test_fail(self):
        """some desc"""
        self.assertEqual(5, 4)

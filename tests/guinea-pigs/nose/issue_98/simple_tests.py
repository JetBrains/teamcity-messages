import unittest


class SimpleTests(unittest.TestCase):
    @unittest.skip('Skipping')
    def test_two(self):
        assert(1 == 1)

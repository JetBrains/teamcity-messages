import unittest


class TestXXX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raise RuntimeError("RRR")

    def runTest(self):
        assert 1 == 1

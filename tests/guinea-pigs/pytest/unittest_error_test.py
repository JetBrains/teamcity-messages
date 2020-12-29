import unittest


class TestErrorFail(unittest.TestCase):
    def test_error(self):
        raise Exception('oops')


    def test_fail(self):
        self.assertTrue(False)

    def test_fail_diff(self):
        self.assertEqual("A", "B")

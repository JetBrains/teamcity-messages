import unittest


class GuineaPig (unittest.TestCase):
    def test_pass(self):
        pass

    def test_fail(self):
        assert 2 * 2 == 5

    def test_fail_with_msg(self):
        assert 2 * 2 == 5, "Bitte keine Werbung"

    def test_fail_output(self):
        print("Output line 1")
        print("Output line 2")
        print("Output line 3")
        assert 2 * 2 == 5

    def test_fail_big_output(self):
        import sys

        sys.stdout.write("x" * (2 * 1024 * 1024))

        assert 2 * 2 == 5

    def test_equals_fail(self):
        from nose.tools import assert_equals
        assert_equals("That is actual", "That was expected")

    def test_equals_fail_with_msg(self):
        from nose.tools import assert_equals
        assert_equals("That is actual", "That was expected", "This is a message")

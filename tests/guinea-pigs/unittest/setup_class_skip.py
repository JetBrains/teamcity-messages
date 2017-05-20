import sys

from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (2, 7):
    from unittest2 import SkipTest, main, TestCase
else:
    from unittest import SkipTest, main, TestCase


class TestSimple(TestCase):

    @classmethod
    def setUpClass(cls):
        raise SkipTest("Skip whole Case")

    def test_true(self):
        self.assertTrue(True)

    def test_false(self):
        self.assertTrue(False, msg="Is not True")

    def test_skip(self):
        raise SkipTest("Skip this test")


class TestSubSimple(TestSimple):

    def test_subclass(self):
        self.assertTrue(True)

main(testRunner=TeamcityTestRunner)

import sys
from teamcity.unittestpy import TeamcityTestRunner

if sys.version_info < (3, 4):
    from unittest2 import main, TestCase
else:
    from unittest import main, TestCase


class NumbersTest(TestCase):
    def test_even(self):
        """Test that numbers between 0 and 5 are all even.
        """
        for i in range(0, 2):
            with self.subTest(i=i):
                self.assertEqual(i % 2, 0)


main(testRunner=TeamcityTestRunner)

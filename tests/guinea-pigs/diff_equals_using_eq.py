import unittest


class Thing(object):

    def __eq__(self, other):
        return True

    def __ne__(self, other):  # Should not be checked because EQ is true
        return True


class TestPycharm(unittest.TestCase):

    def test_equality(self):
        self.assertEqual(Thing(), Thing())


if __name__ == "__main__":
    from teamcity.unittestpy import TeamcityTestRunner

    unittest.main(testRunner=TeamcityTestRunner())

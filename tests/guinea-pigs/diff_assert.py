import unittest



class FooTest(unittest.TestCase):
    def test_test(self):
        self.assertEqual("spam", ("eggs",), "Fail")

    def test_2_test(self):
        self.assertEqual(("eggs",), "spam", "Fail")

    def test_3_test(self):
        self.assertEqual("eggs", "spam", ("Fail",))


if __name__ == "__main__":
    from teamcity.unittestpy import TeamcityTestRunner
    unittest.main(testRunner=TeamcityTestRunner())
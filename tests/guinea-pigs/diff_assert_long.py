import unittest



class FooTest(unittest.TestCase):
    def test_test(self):
        self.assertEqual("spam", "eggs" * 10000, "Fail")

if __name__ == "__main__":
    from teamcity.unittestpy import TeamcityTestRunner
    unittest.main(testRunner=TeamcityTestRunner())
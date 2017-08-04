import unittest



class FooTest(unittest.TestCase):
    def test_test(self):
        self.assertEqual("spam", "eggs", "Fail")

if __name__ == "__main__":
    from teamcity.unittestpy import TeamcityTestRunner
    unittest.main(testRunner=TeamcityTestRunner())
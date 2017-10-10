import unittest



class TestPycharm(unittest.TestCase):
    def test_spam(self):
        with self.subTest('test'):
            self.assertEqual(True, False)


if __name__ == "__main__":
    from teamcity.unittestpy import TeamcityTestRunner
    unittest.main(testRunner=TeamcityTestRunner())
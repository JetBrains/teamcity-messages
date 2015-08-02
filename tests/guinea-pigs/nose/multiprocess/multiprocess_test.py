import unittest
import time


class EvaluateParent(unittest.TestCase):
    _multiprocess_can_split_ = 1

    @classmethod
    def setUpClass(cls):
        print("parent, setUpClass")

    def setUp(self):
        print("parent, setUp")

    def test_pass1_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass3_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass4_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass5_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass6_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass7_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass8_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass9_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass10_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass11_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass12_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_pass2_test(self):
        print("1")
        time.sleep(5)
        self.assertTrue(True)

    def test_timeout0_test(self):
        """Doc test"""
        print("going")
        time.sleep(1)
        raise RuntimeError("error1")

    def test_timeout1_test(self):
        """Doc test"""
        print("going")
        time.sleep(1)
        raise RuntimeError("error1")

    def test_timeout2_test(self):
        """Doc test"""
        print("going")
        time.sleep(1)
        raise RuntimeError("error1")

if __name__ == "__main__":
    unittest.main()

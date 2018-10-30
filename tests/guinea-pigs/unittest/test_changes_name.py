import unittest

from teamcity.unittestpy import TeamcityTestRunner


class Foo(unittest.TestCase):
    a = 1


    def test_aa(self): pass


    def shortDescription(self):
        s = str(self.a)
        self.a += 10
        return s


unittest.main(testRunner=TeamcityTestRunner())

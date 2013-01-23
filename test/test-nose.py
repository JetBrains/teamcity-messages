# coding=utf-8

case_data = [1,2,3]

def checkValue(value):
    assert value == 2

def test_cases():
    for case in case_data:
        yield checkValue, case

class TestTeamcityMessages:
    def testPass(self):
        pass

    def testAssertEqual(self):
        assert 1 == 2

    def testAssert(self):
        assert False

    def testException(self):
        raise Exception("some exception")

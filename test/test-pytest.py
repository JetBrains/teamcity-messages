# coding=utf-8


class TestTeamcityMessages:
    def testPass(self):
        pass

    def testAssertEqual(self):
        assert (True is True)

    def testAssertEqualFails(self):
        assert 1 == 2

    def testAssertFalse(self):
        assert False

    def testException(self):
        raise Exception("some exception")

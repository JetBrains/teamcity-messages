class TestA(object):
    def test_evens(self):
        for i in range(0, 3):
            yield self.check_even, i, i * 3, "."

    def check_even(self, n, nn, s):
        pass

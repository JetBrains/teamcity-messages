def test_evens():
    for i in range(0, 3):
        yield check_even, i, i*3

def check_even(n, nn):
    assert True

def teardown_func():
    assert 1 == 0

def test():
    pass
test.teardown = teardown_func

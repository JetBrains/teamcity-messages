from nose.plugins.skip import SkipTest

def test_func():
    raise SkipTest('my skip')

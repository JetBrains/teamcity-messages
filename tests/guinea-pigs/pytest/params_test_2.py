import pytest


# noinspection PyUnusedLocal
@pytest.mark.parametrize(("_1", "_2"), [
    (None, 'https://facebook.com/'),
    (None, 'https://facebook.com/share.php?http://foo.com/')
])
def test(_1, _2):
    pass

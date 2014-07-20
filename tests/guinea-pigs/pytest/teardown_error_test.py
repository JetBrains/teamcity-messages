import pytest


@pytest.fixture
def fix(request):
    def fin():
        raise Exception('teardown oops')


    request.addfinalizer(fin)
    return 1


def test_error(fix):
    assert fix == 1

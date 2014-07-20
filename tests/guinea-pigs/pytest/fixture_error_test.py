import pytest


@pytest.fixture
def fix():
    raise Exception('oops')


def test_error1(fix):
    assert fix == 1


def test_error2(fix):
    assert fix == 2

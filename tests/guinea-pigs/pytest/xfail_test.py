import pytest


@pytest.mark.xfail("True", reason="xfail reason")
def test_unexpectedly_passing():
    pass


@pytest.mark.xfail("True", reason="xfail reason")
def test_expected_to_fail():
    assert False

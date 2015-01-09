import pytest


@pytest.mark.parametrize(("input", "expected"), [
    ("3+5", 8),
    ("'1.5' + '2'", '1.52'),
    ("6*9", 42),
])
def test_eval(input, expected):
    assert eval(input) == expected

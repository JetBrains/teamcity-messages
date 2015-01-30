from .funcs import covered_func, uncovered_func


def test_covered_func():
    func = covered_func()
    assert func == 3

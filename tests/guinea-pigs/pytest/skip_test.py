# coding=utf-8
import pytest


@pytest.mark.skipif("True", reason=u"skip reason причина")
def test_function():
    pass

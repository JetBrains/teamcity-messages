import pytest

def test_cp():
    assert 'Ф'.encode('utf8') != b'\xd0\xa4'
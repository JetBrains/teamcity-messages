from unittest.mock import Mock


def test_test():
    m = Mock()
    m('foo')
    m.assert_called_with('bar')

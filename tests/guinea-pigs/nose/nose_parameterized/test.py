from nose_parameterized import parameterized


# noinspection PyUnusedLocal
@parameterized([
    ("1.1", "https://facebook.com/share.php?http://foo.com/"),
    (None, 3),
])
def test(_1, _2):
    pass

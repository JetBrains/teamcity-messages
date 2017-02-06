from nose_parameterized import parameterized


# noinspection PyUnusedLocal
@parameterized([
    ("1.1", "1.2"),
    (None, 3),
])
def test(_1, _2):
    pass

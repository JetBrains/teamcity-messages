from flask_testing import TestCase


# throws NotImplementedError since create_app is not implemented
class TestIncompleteFoo(TestCase):
    def test_add(self):
        self.assertEqual(1 + 2, 3)

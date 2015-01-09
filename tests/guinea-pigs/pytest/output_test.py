import pytest
import sys


@pytest.fixture
def fix(request):
    def fin():
        sys.stdout.write("teardown stdout\n")
        sys.stderr.write("teardown stderr\n")

    sys.stdout.write("setup stdout\n")
    sys.stderr.write("setup stderr\n")
    request.addfinalizer(fin)
    return 1


def test_out(fix):
    sys.stdout.write("test stdout\n")
    sys.stderr.write("test stderr\n")
    assert fix == 1

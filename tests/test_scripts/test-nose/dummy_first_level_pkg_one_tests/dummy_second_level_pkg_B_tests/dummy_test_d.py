import sys
from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke')
def test_dummy_in_development_with_assertion_error():
    sys.stdout.write("stdout string\n")
    sys.stderr.write("stderr string\n")
    assert False


@attr('demo_smoke', 'smoke')
def test_dummy_in_development_with_assertion_pass():
    assert True
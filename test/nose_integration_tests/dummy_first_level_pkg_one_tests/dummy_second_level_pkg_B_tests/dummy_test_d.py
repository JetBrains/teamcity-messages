from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke')
def test_dummy_in_development_with_assertion_error():
    assert False

@attr('demo_smoke', 'smoke')
def test_dummy_in_development_with_assertion_pass():
    assert True
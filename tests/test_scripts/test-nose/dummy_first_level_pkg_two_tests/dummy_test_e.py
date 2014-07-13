from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke', 'known_good')
def test_dummy_known_good_with_assertion_pass():
    assert True
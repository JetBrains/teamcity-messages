from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke', 'known_good')
def test_dummy_known_good_with_assertion_pass():
    """
    test_dummy_known_good_with_assertion_pass
    I'd like to buy the world a coke!
    """
    assert True
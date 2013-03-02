from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke', 'known_bad')
def test_dummy_known_bad_with_assertion_error():
    """
    test_dummy_known_bad_with_assertion_error
    I'd like to buy the world a Dr Pepper!
    """
    assert False

@attr('demo_smoke', 'smoke', 'known_bad')
def test_dummy_known_bad_with_assertion_pass():
    """
    test_dummy_known_bad_with_assertion_pass
    I'd like to buy the world a Mr. Pib!
    """
    assert True

@attr('demo_smoke', 'smoke', 'known_bad')
def test_dummy_known_bad_with_language_error():
    """
    test_dummy_known_bad_with_language_error
    I'd like to buy the world a RC Cola!
    """
    non_existent_method_123()
    assert True
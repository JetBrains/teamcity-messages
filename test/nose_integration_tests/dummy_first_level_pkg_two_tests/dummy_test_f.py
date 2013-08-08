from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke', 'known_bad')
def test_dummy_known_bad_with_assertion_error():
    assert False


@attr('demo_smoke', 'smoke', 'known_bad')
def test_dummy_known_bad_with_assertion_pass():
    assert True


@attr('demo_smoke', 'smoke', 'known_bad')
def test_dummy_known_bad_with_language_error():
    non_existent_method_123()
    assert True
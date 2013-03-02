from nose.plugins.attrib import attr

#The method below doesn't exist and is intentionally defined
#outside of a method. Consequently, nose will blow up before
#there is even a chance to define the test method.
evil_non_existent_method_123G()

@attr('demo_smoke', 'smoke', 'known_good')
def test_dummy_g_never_gets_called():
    """
    test that will never be defined
    """
    assert True
from nose.plugins.attrib import attr


@attr('demo_smoke', 'smoke', 'known_good')
def test_dummy_known_good_with_assertion_pass():
    assert True

def test_with_generator():
    for i in range (0, 5):
        yield do_something, i

def do_something(i):
    assert True, "do something number: {}".format(i)

def test_with_generator_and_pydoc():
    """
    Tests that have pydoc are cool
    """
    for i in range (0, 5):
        @attr(description="Do not worry, be happy {}".format(i))
        def wrapper(*args, **kwargs):
            do_something_else(*args, **kwargs)
        yield wrapper, i

def do_something_else(i):
    """
    Let's do something else instead.
    """
    assert True, "do something else number: {}".format(i)


@attr(description="generators with pydoc and descriptions are the most funky")
def test_with_generator_and_description_and_pydoc():
    """
    Tests that have pydoc are cool
    """
    for i in range (0, 5):
        @attr(description="Do not worry, be funky {}".format(i))
        def wrapper(*args, **kwargs):
            do_something_funky(*args, **kwargs)
        yield wrapper, i

def do_something_funky(i):
    """
    Let's do something funky instead.
    """
    if i==1:
        assert False, "i do not want to be funky just yet {}".format(i)
    elif i==2:
        evil_non_existent_method()
    else:
        assert True, "do something funky number: {}".format(i)


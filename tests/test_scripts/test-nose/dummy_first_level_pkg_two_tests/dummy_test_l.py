import unittest
#from nose.plugins.attrib import attr


class DummyTestL(unittest.TestCase):
    """Today is brought to you by the letter L"""

    def test_something(self):
        """
        Lizards love testing
        Lizards have very long tongues.
        """
        self.assertTrue(True, 'example assertion')

    #Attributes don't work in subclasses of unittest.TestCase
    #@attr(description="Lanky developers are not lanky anymore")
    def test_something_else(self):
        """
        Lanky developers love testing.
        """
        self.assertTrue(True, 'example assertion')

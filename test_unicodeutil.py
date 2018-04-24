#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from unicodeutil import CaseFoldingMap, casefold


class TestCaseFoldingMap(unittest.TestCase):
    """Class for testing the CaseFoldingMap() class."""

    def setUp(self):
        """Shared setup for all tests."""
        self.casefoldingmap = CaseFoldingMap()

    def test_default_lookup(self):
        """Test the default behavior of the call to lookup()."""
        self.assertEqual(u"ss", self.casefoldingmap.lookup(u"ß"))
        self.assertEqual(u"i\u0307", self.casefoldingmap.lookup(u"İ"))
        self.assertEqual(u"ss", self.casefoldingmap.lookup(u"ẞ"))

    def test_simple_lookup(self):
        """Test the behavior of a simple casefold call to lookup()."""
        self.assertEqual(u"ß", self.casefoldingmap.lookup(u"ß", lookup_order="CS"))
        self.assertEqual(u"İ", self.casefoldingmap.lookup(u"İ", lookup_order="CS"))
        self.assertEqual(u"ß", self.casefoldingmap.lookup(u"ẞ", lookup_order="CS"))

    def test_full_lookup(self):
        """Test the behavior of a full casefold call to lookup()."""
        self.assertEqual(u"ss", self.casefoldingmap.lookup(u"ß", lookup_order="CF"))
        self.assertEqual(u"i\u0307", self.casefoldingmap.lookup(u"İ", lookup_order="CF"))
        self.assertEqual(u"ss", self.casefoldingmap.lookup(u"ẞ", lookup_order="CF"))

    def test_turkish_lookup(self):
        """Test the behavior of a turkish casefold call to lookup()."""
        # LATIN CAPITAL LETTER I
        self.assertEqual(u"ı", self.casefoldingmap.lookup(u"I", lookup_order="TCF"))
        self.assertEqual(u"ı", self.casefoldingmap.lookup(u"I", lookup_order="TCS"))
        # LATIN CAPITAL LETTER I WITH DOT ABOVE
        self.assertEqual(u"i", self.casefoldingmap.lookup(u"İ", lookup_order="TCF"))
        self.assertEqual(u"i", self.casefoldingmap.lookup(u"İ", lookup_order="TCS"))


class TestCasefold(unittest.TestCase):
    """Class for testing the casefold() function."""

    def test_default_casefold(self):
        """
        This test is based on the str.casefold() tests for python 3. Source:
        https://github.com/python/cpython/blob/6f870935c2e024cbd1cc379f85e6a66d7711dcc7/Lib/test/test_unicode.py#L770
        """
        self.assertEqual(casefold(u"hello"), u"hello")
        self.assertEqual(casefold(u"hELlo"), u"hello")
        self.assertEqual(casefold(u"ß"), u"ss")
        self.assertEqual(casefold(u"ﬁ"), u"fi")
        self.assertEqual(casefold(u"\u03a3"), u"\u03c3")  # GREEK CAPITAL LETTER SIGMA
        self.assertEqual(casefold(u"A\u0345\u03a3"), u"a\u03b9\u03c3")  # COMBINING GREEK YPOGEGRAMMENI
        self.assertEqual(casefold(u"\u00b5"), u"\u03bc")  # MICRO SIGN

    def test_default_casefold_non_unicode(self):
        """Test that passing a non-unicode string causes an exception to be raised."""
        self.assertRaises(TypeError, casefold, "I")
        self.assertRaises(TypeError, casefold, "hello")

    def test_simple_casefold(self):
        """Test for simple casefolding."""
        self.assertEqual(u"weiß", casefold(u"weiß", fullcasefold=False))
        self.assertEqual(u"weiß", casefold(u"WEIẞ", fullcasefold=False))
        # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
        self.assertEqual(u"\u0390", casefold(u"\u0390", fullcasefold=False))
        # GREEK CAPITAL LETTER ALPHA WITH PSILI AND PROSGEGRAMMENI
        self.assertEqual(u"\u1f80", casefold(u"\u1f88", fullcasefold=False))

    def test_full_casefold(self):
        """Test for full casefolding (explicitly specifying fullcasefold=True)."""
        self.assertEqual(u"weiss", casefold(u"weiß", fullcasefold=True))
        self.assertEqual(u"weiss", casefold(u"WEIẞ", fullcasefold=True))
        # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
        self.assertEqual(u"\u03b9\u0308\u0301", casefold(u"\u0390", fullcasefold=True))
        # GREEK CAPITAL LETTER ALPHA WITH PSILI AND PROSGEGRAMMENI
        self.assertEqual(u"\u1f00\u03b9", casefold(u"\u1f88", fullcasefold=True))


if __name__ == "__main__":
    unittest.main()

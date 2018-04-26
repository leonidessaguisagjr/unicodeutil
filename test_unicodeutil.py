#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates


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

    def test_simple_lookup_surrogate_pair(self):
        """Test the behavior of a simple casefold call to lookup() using a surrogate pair."""
        # DESERET CAPITAL LETTER LONG I
        self.assertEqual(u"\U00010428", self.casefoldingmap.lookup(u"\U00010400", lookup_order="CS"))
        # OLD HUNGARIAN CAPITAL LETTER NIKOLSBURG OE
        self.assertEqual(u"\U00010428", self.casefoldingmap.lookup(u"\U00010400", lookup_order="CS"))
        # ADLAM CAPITAL LETTER ALIF
        self.assertEqual(u"\U00010cdd", self.casefoldingmap.lookup(u"\U00010c9d", lookup_order="CS"))

    def test_full_lookup(self):
        """Test the behavior of a full casefold call to lookup()."""
        self.assertEqual(u"ss", self.casefoldingmap.lookup(u"ß", lookup_order="CF"))
        self.assertEqual(u"i\u0307", self.casefoldingmap.lookup(u"İ", lookup_order="CF"))
        self.assertEqual(u"ss", self.casefoldingmap.lookup(u"ẞ", lookup_order="CF"))

    def test_full_lookup_surrogate_pair(self):
        """Test the behavior of a full casefold call to lookup() using a surrogate pair."""
        # DESERET CAPITAL LETTER LONG I
        self.assertEqual(u"\U00010428", self.casefoldingmap.lookup(u"\U00010400", lookup_order="CF"))
        # OLD HUNGARIAN CAPITAL LETTER NIKOLSBURG OE
        self.assertEqual(u"\U00010428", self.casefoldingmap.lookup(u"\U00010400", lookup_order="CF"))
        # ADLAM CAPITAL LETTER ALIF
        self.assertEqual(u"\U00010cdd", self.casefoldingmap.lookup(u"\U00010c9d", lookup_order="CF"))

    def test_turkish_lookup(self):
        """Test the behavior of a turkish casefold call to lookup()."""
        # LATIN CAPITAL LETTER I
        self.assertEqual(u"ı", self.casefoldingmap.lookup(u"I", lookup_order="TCF"))
        self.assertEqual(u"ı", self.casefoldingmap.lookup(u"I", lookup_order="TCS"))
        # LATIN CAPITAL LETTER I WITH DOT ABOVE
        self.assertEqual(u"i", self.casefoldingmap.lookup(u"İ", lookup_order="TCF"))
        self.assertEqual(u"i", self.casefoldingmap.lookup(u"İ", lookup_order="TCS"))


class TestUnicodeData(unittest.TestCase):
    """Class for testing the UnicodeData() class."""

    def setUp(self):
        """Shared setup for all tests."""
        self.ucd = UnicodeData()

    def test_lookup(self):
        """Test the default lookup behavior."""
        self.assertEqual(u"LATIN CAPITAL LETTER I WITH DOT ABOVE", self.ucd[u"İ"].name)
        self.assertEqual(0, self.ucd[u"0"].decimal)
        self.assertEqual(1, self.ucd[u"1"].digit)
        self.assertEqual(2, self.ucd[u"2"].numeric)
        self.assertEqual(u"BACKSLASH", self.ucd[u"\\"].unicode_1_name)
        self.assertEqual(u"A", self.ucd[u"a"].uppercase)
        self.assertEqual(u"z", self.ucd[u"Z"].lowercase)
        self.assertEqual(u"ǅ", self.ucd[u"Ǆ"].titlecase)

    def test_lookup_by_name(self):
        """Test looking up by name."""
        expected = self.ucd[u"ß"]
        self.assertEqual(expected, self.ucd.lookup_by_name("LATIN SMALL LETTER SHARP S"))
        self.assertEqual(expected, self.ucd.lookup_by_name("LATIN_SMALL_LETTER_SHARP_S"))
        self.assertEqual(expected, self.ucd.lookup_by_name("latin_small_letter_sharp_s"))
        self.assertEqual(expected, self.ucd.lookup_by_name("latinsmalllettersharps"))
        expected = self.ucd[unichr(0x200c)]
        self.assertEqual(expected, self.ucd.lookup_by_name("ZERO WIDTH NON-JOINER"))
        self.assertEqual(expected, self.ucd.lookup_by_name("ZERO_WIDTH_NON-JOINER"))
        self.assertEqual(expected, self.ucd.lookup_by_name("ZERO_WIDTH_NON_JOINER"))
        self.assertEqual(expected, self.ucd.lookup_by_name("Zero Width Non-Joiner"))
        self.assertEqual(expected, self.ucd.lookup_by_name("zero width non-joiner"))
        self.assertEqual(expected, self.ucd.lookup_by_name("zero width non joiner"))

    def test_name_lookup_neg(self):
        """Test for verifying that looking for a non-existent name causes a KeyError to be raised."""
        self.assertRaises(KeyError, self.ucd.lookup_by_name, "THIS IS A NON-EXISTENT NAME")

    def test_lookup_nonchar(self):
        """
        Test that looking up a noncharacter raises a KeyError.

        See https://www.unicode.org/faq/private_use.html#nonchar1 for more info on Unicode noncharacters.
        """
        self.assertRaises(KeyError, self.ucd.get, unichr(0xFDD0))
        self.assertRaises(KeyError, self.ucd.get, unichr(0xFDEF))

    def test_get_getitem(self):
        """Test that calls to get() and __getitem__() return the same data."""
        self.assertEqual(self.ucd.get(u"ẞ"), self.ucd[u"ẞ"])


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

    def test_simple_casefold_surrogate_pair(self):
        """Test for simple casefolding of a string with surrogate pairs."""
        # A; B; OSAGE CAPITAL LETTER A; C; D; WARANG CITI CAPITAL LETTER NGAA; E; F
        self.assertEqual(u"ab\U000104D8cd\U000118C0ef", casefold(u"AB\U000104B0CD\U000118A0EF", fullcasefold=False))

    def test_full_casefold(self):
        """Test for full casefolding (explicitly specifying fullcasefold=True)."""
        self.assertEqual(u"weiss", casefold(u"weiß", fullcasefold=True))
        self.assertEqual(u"weiss", casefold(u"WEIẞ", fullcasefold=True))
        # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
        self.assertEqual(u"\u03b9\u0308\u0301", casefold(u"\u0390", fullcasefold=True))
        # GREEK CAPITAL LETTER ALPHA WITH PSILI AND PROSGEGRAMMENI
        self.assertEqual(u"\u1f00\u03b9", casefold(u"\u1f88", fullcasefold=True))

    def test_full_casefold_surrogate_pair(self):
        """Test for full casefolding of a string with surrogate pairs."""
        # A; B; OSAGE CAPITAL LETTER A; C; D; WARANG CITI CAPITAL LETTER NGAA; E; F
        self.assertEqual(u"ab\U000104D8cd\U000118C0ef", casefold(u"AB\U000104B0CD\U000118A0EF", fullcasefold=True))

    def test_turkic_casefold(self):
        """Test for casefolding with the useturkicmapping parameter."""
        s1 = u"DİYARBAKIR"
        s2 = u"Diyarbakır"
        self.assertNotEqual(casefold(s1), casefold(s2))
        self.assertEqual(casefold(s1, useturkicmapping=True), casefold(s2, useturkicmapping=True))
        s1 = u"MISSISSIPPI"
        s2 = u"mississippi"
        self.assertEqual(casefold(s1), casefold(s2))
        self.assertNotEqual(casefold(s1, useturkicmapping=True), casefold(s2, useturkicmapping=True))


class TestPreserveSurrogates(unittest.TestCase):
    """Class for testing the preservesurrogates(s) function."""

    def test_preservesurrogates(self):
        """Positive test for preservesurrogates() functionality."""
        test_input = u"ABC\U0001e900DeF\U000118a0gHıİ"
        expected = [u'A', u'B', u'C', u'\U0001e900', u'D', u'e', u'F', u'\U000118a0', u'g', u'H', u'ı', u'İ']
        actual = preservesurrogates(test_input)
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_preservesurrogates_non_unicode(self):
        """Test that passing a non-unicode string causes an exception to be raised."""
        self.assertRaises(TypeError, preservesurrogates, "ABCDEF")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import six

from unicodeutil import CaseFoldingMap, UnicodeBlocks, UnicodeData, casefold, compose_hangul_syllable, decompose_hangul_syllable, \
    preservesurrogates
from unicodeutil.unicodeutil import _nr_prefix_strings, _padded_hex, _unichr
from unicodeutil.hangulutil import _get_hangul_syllable_name


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
        self.assertEqual(u"LATIN CAPITAL LETTER I WITH DOT ABOVE", self.ucd[0x0130].name)
        self.assertEqual(0, self.ucd[0x0030].decimal)  # DIGIT ZERO
        self.assertEqual(1, self.ucd[0x0031].digit)  # DIGIT ONE
        self.assertEqual(2, self.ucd[0x0032].numeric)  # DIGIT TWO
        self.assertEqual(u"BACKSLASH", self.ucd[0x005c].unicode_1_name)  # REVERSE SOLIDUS
        self.assertEqual(u"A", self.ucd[0x0061].uppercase)  # LATIN SMALL LETTER A
        self.assertEqual(u"z", self.ucd[0x005a].lowercase)  # LATIN CAPITAL LETTER Z
        self.assertEqual(u"ǅ", self.ucd[0x01c4].titlecase)  # LATIN CAPITAL LETTER DZ WITH CARON

    def test_lookup_by_char(self):
        """Test look up by Unicode character."""
        self.assertEqual(u"REVERSE SOLIDUS", self.ucd.lookup_by_char(u"\\").name)
        self.assertEqual(u"YEN SIGN", self.ucd.lookup_by_char(u"¥").name)
        self.assertEqual(u"LATIN CAPITAL LETTER SHARP S", self.ucd.lookup_by_char(u"ẞ").name)
        self.assertEqual(u"TAGALOG LETTER BA", self.ucd.lookup_by_char(u"ᜊ").name)
        self.assertEqual(u"HANGUL SYLLABLE GA", self.ucd.lookup_by_char(u"가").name)
        self.assertEqual(u"LINEAR B SYLLABLE B008 A", self.ucd.lookup_by_char(u"𐀀").name)
        self.assertEqual(u"CJK UNIFIED IDEOGRAPH-20000", self.ucd.lookup_by_char(u"𠀀").name)

    def test_lookup_by_name(self):
        """Test looking up by name."""
        expected = self.ucd[0x00df]
        self.assertEqual(expected, self.ucd.lookup_by_name("LATIN SMALL LETTER SHARP S"))
        self.assertEqual(expected, self.ucd.lookup_by_name("LATIN_SMALL_LETTER_SHARP_S"))
        self.assertEqual(expected, self.ucd.lookup_by_name("latin_small_letter_sharp_s"))
        self.assertEqual(expected, self.ucd.lookup_by_name("latinsmalllettersharps"))
        expected = self.ucd[0x200c]
        self.assertEqual(expected, self.ucd.lookup_by_name("ZERO WIDTH NON-JOINER"))
        self.assertEqual(expected, self.ucd.lookup_by_name("ZERO_WIDTH_NON-JOINER"))
        self.assertEqual(expected, self.ucd.lookup_by_name("ZERO_WIDTH_NON_JOINER"))
        self.assertEqual(expected, self.ucd.lookup_by_name("Zero Width Non-Joiner"))
        self.assertEqual(expected, self.ucd.lookup_by_name("zero width non-joiner"))
        self.assertEqual(expected, self.ucd.lookup_by_name("zero width non joiner"))
        expected = self.ucd[0x1705]
        self.assertEqual(expected, self.ucd.lookup_by_name("TAGALOG LETTER NGA"))
        self.assertEqual(expected, self.ucd.lookup_by_name("TAGALOG_LETTER_NGA"))
        self.assertEqual(expected, self.ucd.lookup_by_name("tagalog-letter-nga"))
        self.assertEqual(expected, self.ucd.lookup_by_name("tagalog_letter nga"))

    def test_name_lookup_neg(self):
        """Test for verifying that looking for a non-existent name causes a KeyError to be raised."""
        self.assertRaises(KeyError, self.ucd.lookup_by_name, "THIS IS A NON-EXISTENT NAME")

    def test_lookup_nonchar(self):
        """
        Test that looking up a noncharacter raises a KeyError.

        See https://www.unicode.org/faq/private_use.html#nonchar1 for more info on Unicode noncharacters.
        """
        self.assertRaises(KeyError, self.ucd.get, 0xFDD0)
        self.assertRaises(KeyError, self.ucd.get, 0xFDEF)

    def test_lookup_by_partial_name(self):
        """Test lookup by partial name."""
        partial_name = "SHARP S"
        for data in self.ucd.lookup_by_partial_name(partial_name):
            self.assertTrue(partial_name in data.name)
        char_info_list = list(self.ucd.lookup_by_partial_name("NON EXISTENT CHARACTER"))
        self.assertFalse(char_info_list)

    def test_get_getitem(self):
        """Test that calls to get() and __getitem__() return the same data."""
        self.assertEqual(self.ucd.get(0x1e9e), self.ucd[0x1e9e])  # LATIN CAPITAL LETTER SHARP S

    def test_lookup_compressed_char(self):
        """
        Test that looking up characters in the "compressed" ranges of UnicodeData.txt are successful.  See the Unicode
        Standard, ch. 4, section 4.8 for more information on how the compression works.
        """
        # Test naming rule NR1 with an example from Unicode Standard, ch. 03, section 3.12
        self.assertEqual("HANGUL SYLLABLE PWILH", self.ucd[0xD4DB].name)
        # Go through each range and test characters from the start, middle and end of the ranges
        for lookup_range, prefix_string in _nr_prefix_strings.items():
            start_range = lookup_range[0]
            end_range = lookup_range[-1]
            range_size = end_range - start_range
            mid_range = start_range + (range_size // 2)
            quarter_range = start_range + (range_size // 4)
            three_quarter_range = start_range + (range_size * 3 // 4)
            test_ranges = [start_range, quarter_range, mid_range, three_quarter_range, end_range]
            for item in test_ranges:
                char_info = self.ucd[item]
                if prefix_string.startswith("HANGUL SYLLABLE"):  # Check for naming rule NR1
                    self.assertEqual(prefix_string + _get_hangul_syllable_name(item), char_info.name)
                else:  # Check for naming rule NR2
                    self.assertEqual(prefix_string + _padded_hex(item), char_info.name)


class TestUnicodeBlocks(unittest.TestCase):
    """Class for testing the UnicodeBlocks() class."""

    def setUp(self):
        """Shared setup for all tests."""
        self.blocks = UnicodeBlocks()

    def test_getitem(self):
        """Test that dict style lookup succeeds."""
        self.assertEqual(u"Basic Latin", self.blocks[0x007F])

    def test_get(self):
        """Test that calling get() succeeds."""
        self.assertEqual(u"Latin-1 Supplement", self.blocks[0x00FF])

    def test_lookup_by_char(self):
        """Test that calling lookup_by_char() succeeds."""
        self.assertEqual(u"Latin Extended Additional", self.blocks.lookup_by_char(u"ẞ"))

    def test_noblock(self):
        """Test that attempting to lookup an undefined character generates a 'No_Block'."""
        self.assertEqual(u"No_Block", self.blocks[0x31350])


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
        self.assertRaises(TypeError, casefold, "I".encode("utf-8"))
        self.assertRaises(TypeError, casefold, "hello".encode("utf-8"))

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
        self.assertRaises(TypeError, preservesurrogates, "ABCDEF".encode("utf-8"))


class TestGetHangulSyllableName(unittest.TestCase):
    """Class for testing the _get_hangul_syllable_name(hangul_syllable) function."""

    def test_lookup(self):
        """Test that lookup works and the correct syllable names are returned."""
        # Example from the Unicode Standard, ch. 03, section 3.12
        self.assertEqual("PWILH", _get_hangul_syllable_name(0xD4DB))
        # Examples from the start, middle and end of the Hangul syllable range
        self.assertEqual("GA", _get_hangul_syllable_name(0xAC00))
        self.assertEqual("DDWELM", _get_hangul_syllable_name(0xB6DE))
        self.assertEqual("SWAELT", _get_hangul_syllable_name(0xC1D1))
        self.assertEqual("CENH", _get_hangul_syllable_name(0xCCBA))
        self.assertEqual("HIH", _get_hangul_syllable_name(0xD7A3))


class TestDecomposeHangulSyllable(unittest.TestCase):
    """Class for testing the decompose_hangul_syllable(hangul_syllable) function."""

    def test_decompose_hangul_syllable_default(self):
        """Test that the default decomposition works."""
        # Example from Unicode Standard, ch. 03, section 3.12
        self.assertEqual((0xD4CC, 0x11B6), decompose_hangul_syllable(0xD4DB))
        self.assertEqual((0x1111, 0x1171), decompose_hangul_syllable(0xD4CC))
        # Example from Unicode® Standard Annex #44, https://unicode.org/reports/tr44/#Character_Decomposition_Mappings
        self.assertEqual((0xCE20, 0x11B8), decompose_hangul_syllable(0xCE31))
        self.assertEqual((0x110E, 0x1173), decompose_hangul_syllable(0xCE20))

    def test_decompose_hangul_syllable_canonical_decomposition(self):
        """Test that the decomposition works if we explicitly set fully_decompose=False."""
        # Example from Unicode Standard, ch. 03, section 3.12
        self.assertEqual((0xD4CC, 0x11B6), decompose_hangul_syllable(0xD4DB, fully_decompose=False))
        self.assertEqual((0x1111, 0x1171), decompose_hangul_syllable(0xD4CC, fully_decompose=False))
        # Example from Unicode® Standard Annex #44, https://unicode.org/reports/tr44/#Character_Decomposition_Mappings
        self.assertEqual((0xCE20, 0x11B8), decompose_hangul_syllable(0xCE31, fully_decompose=False))
        self.assertEqual((0x110E, 0x1173), decompose_hangul_syllable(0xCE20, fully_decompose=False))

    def test_decompose_hangul_syllable_full_canonical_decomposition(self):
        """Test that the decomposition works if we explicitly set fully_decompose=True."""
        # Example from Unicode Standard, ch. 03, section 3.12
        self.assertEqual((0x1111, 0x1171, 0x11B6), decompose_hangul_syllable(0xD4DB, fully_decompose=True))
        self.assertEqual((0x1111, 0x1171, None), decompose_hangul_syllable(0xD4CC, fully_decompose=True))
        # Example from Unicode® Standard Annex #44, https://unicode.org/reports/tr44/#Character_Decomposition_Mappings
        self.assertEqual((0x110E, 0x1173, 0x11B8), decompose_hangul_syllable(0xCE31, fully_decompose=True))
        self.assertEqual((0x110E, 0x1173, None), decompose_hangul_syllable(0xCE20, fully_decompose=True))


class TestComposeHangulSyllable(unittest.TestCase):
    """Class for testing the compose_hangul_syllable(jamo) function."""

    def test_compose_hangul_syllable_l_v(self):
        """Test that composing from an (l_part, t_part) tuple is successful."""
        self.assertEqual(0xD4CC, compose_hangul_syllable((0x1111, 0x1171)))

    def test_compose_hangul_syllable_l_v_t(self):
        """Test that composing from an (l_part, v_part, t_part) tuple is successful."""
        self.assertEqual(0xD4DB, compose_hangul_syllable((0x1111, 0x1171, 0x11B6)))

    def test_compose_hangul_syllable_lv_t(self):
        """Test that composing from an (lv_part, t_part) tuple is successful."""
        self.assertEqual(0xD4DB, compose_hangul_syllable((0xD4CC, 0x11B6)))

    def test_compose_hangul_syllable_neg(self):
        """Test that passing in invalid sequences correctly raise a ValueError."""
        self.assertRaises(ValueError, compose_hangul_syllable, (0x1111, ))  # 1-element tuple
        self.assertRaises(ValueError, compose_hangul_syllable, (0x1111, 0x1171, 0xD4CC, 0x11B6))  # 4-element tuple
        self.assertRaises(ValueError, compose_hangul_syllable, (0x1111, 0x11B6))  # (l_part, t_part) tuple
        self.assertRaises(ValueError, compose_hangul_syllable, (0x0061, 0x0300))  # non-Jamo characters
        self.assertRaises(ValueError, compose_hangul_syllable, (0x0073, 0x0323, 0x0307))  # non-Jamo characters


if __name__ == "__main__":
    unittest.main()

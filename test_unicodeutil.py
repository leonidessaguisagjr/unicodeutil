#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from unicodeutil import casefold


class TestCasefold(unittest.TestCase):
    """Class for testing the casefold() function."""

    def test_casefold(self):
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
        with self.assertRaises(TypeError):
            casefold("I")


if __name__ == "__main__":
    unittest.main()

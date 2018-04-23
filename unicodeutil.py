#!/usr/bin/env python

import os

_casefold_map = {}


def _hexstr_to_unichr(s):
    """Helper function for taking a hex string and returning a unicode char."""
    try:
        return unichr(int(s, 16))
    except ValueError:
        # Workaround the error "ValueError: unichr() arg not in range(0x10000) (narrow Python build)"
        return ("\\U%08x" % int(s, 16)).decode("unicode-escape")


def _build_casefold_map():
    """
    Function for parsing the case folding data from the Unicode Character
    Database (UCD) and generating a lookup table.  For more info on the UCD,
    see the following website: https://www.unicode.org/ucd/
    """
    global _casefold_map
    filename = "CaseFolding.txt"
    current_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(current_dir, filename), "rb") as fp:
        for line in fp:
            if not line.strip() or line.startswith("#"):
                continue  # Skip empty lines or lines that are comments (comments start with '#')
            code, status, mapping, name = line.split(";")
            if status.strip() not in "CF":
                continue  # Skip entries not related to full case folding.
            src = _hexstr_to_unichr(code)
            target = "".join([_hexstr_to_unichr(c) for c in mapping.strip().split()])
            _casefold_map[src] = target


def casefold(s):
    """
    Function for performing full case folding.  This function will take the input
    string s and return a copy of the string suitable for caseless comparisons.
    The input string must be of type 'unicode', otherwise a TypeError will be
    raised.

    For more information on case folding, see section 3.13 of the Unicode Standard.
    See also the following FAQ on the Unicode website:

    https://unicode.org/faq/casemap_charprop.htm

    :param s: String to transform
    :return: Copy of string that has been transformed for caseless comparison.
    """
    if not isinstance(s, unicode):
        raise TypeError("String to casefold must be of type 'unicode'!")
    if not _casefold_map:
        _build_casefold_map()
    return u"".join([_casefold_map.get(c, c) for c in s])

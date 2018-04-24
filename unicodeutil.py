#!/usr/bin/env python

from collections import defaultdict
import os


class CaseFoldingMap:
    """Class for performing Unicode case folding."""

    def __init__(self):
        """Initialize the class by building the casefold map."""
        self._build_casefold_map()

    def _hexstr_to_unichr(self, s):
        """
        Helper function for taking a hex string and returning a unicode char.

        :param s: hex string to convert
        :return: unicode character
        """
        try:
            return unichr(int(s, 16))
        except ValueError:
            # Workaround the error "ValueError: unichr() arg not in range(0x10000) (narrow Python build)"
            return ("\\U%08x" % int(s, 16)).decode("unicode-escape")

    def _build_casefold_map(self):
        """
        Function for parsing the case folding data from the Unicode Character
        Database (UCD) and generating a lookup table.  For more info on the UCD,
        see the following website: https://www.unicode.org/ucd/
        """
        self._casefold_map = defaultdict(dict)
        filename = "CaseFolding.txt"
        current_dir = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(current_dir, filename), "rb") as fp:
            for line in fp:
                if not line.strip() or line.startswith("#"):
                    continue  # Skip empty lines or lines that are comments (comments start with '#')
                code, status, mapping, name = line.split(";")
                src = self._hexstr_to_unichr(code)
                target = "".join([self._hexstr_to_unichr(c) for c in mapping.strip().split()])
                self._casefold_map[status.strip()][src] = target

    def lookup(self, c, lookup_order="CF"):
        """
        Function to lookup a character in the casefold map.

        The casefold map has four sub-tables, the 'C' or common table, the 'F' or
        full table, the 'S' or simple table and the 'T' or the Turkic special
        case table.  These tables correspond to the statuses defined in the
        CaseFolding.txt file.  We can specify the order of the tables to use for
        performing the lookup by the lookup_order parameter.

        Per the usage specified in the CaseFolding.txt file, we can use the 'C'
        and 'S' tables for doing a simple case fold.  To perform a full case
        fold, we can use the 'C' and 'F' tables.  The default behavior for this
        function is a full case fold (lookup_order="CF").

        :param c: character to lookup
        :param lookup_order:
        """
        if not isinstance(c, unicode):
            raise TypeError("Character to lookup must be of type 'unicode'!")
        for d in lookup_order:
            try:
                return self._casefold_map[d][c]
            except KeyError:
                pass
        return c


casefold_map = CaseFoldingMap()


def casefold(s, fullcasefold=True):
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
    lookup_order = "CF"
    if not fullcasefold:
        lookup_order = "CS"
    return u"".join([casefold_map.lookup(c, lookup_order=lookup_order) for c in s])

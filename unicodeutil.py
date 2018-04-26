#!/usr/bin/env python

from collections import defaultdict, namedtuple
from fractions import Fraction
import os
import re


HIGH_SURROGATE_START = u"\ud800"
HIGH_SURROGATE_END = u"\udbff"
LOW_SURROGATE_START = u"\udc00"
LOW_SURROGATE_END = u"\udfff"


def preservesurrogates(s):
    """
    Function for splitting a string into a list of characters, preserving surrogate pairs.

    In python 2, unicode characters above 0x10000 are stored as surrogate pairs.  For example, the Unicode character
    u"\U0001e900" is stored as the surrogate pair u"\ud83a\udd00":

    s = u"AB\U0001e900CD"
    len(s) -> 6
    list(s) -> [u'A', u'B', u'\ud83a', u'\udd00', u'C', 'D']
    len(preservesurrogates(s)) -> 5
    list(preservesurrogates(s)) -> [u'A', u'B', u'\U0001e900', u'C', u'D']

    :param s: String to split
    :return: List of characters
    """
    if not isinstance(s, unicode):
        raise TypeError(u"String to split must be of type 'unicode'!")
    surrogates_regex_str = u"[{0}-{1}][{2}-{3}]".format(HIGH_SURROGATE_START,
                                                        HIGH_SURROGATE_END,
                                                        LOW_SURROGATE_START,
                                                        LOW_SURROGATE_END)
    surrogates_regex = re.compile(u"(?:{0})|.".format(surrogates_regex_str))
    return surrogates_regex.findall(s)


def _hexstr_to_unichr(s):
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


# Documentation on the fields of UnicodeData.txt:
# https://www.unicode.org/L2/L1999/UnicodeData.html
# https://www.unicode.org/reports/tr44/#UnicodeData.txt
UnicodeCharacter = namedtuple("UnicodeCharacter", ["name", "category", "combining", "bidi", "decomposition",
                                                   "decimal", "digit", "numeric", "mirrored", "unicode_1_name",
                                                   "iso_comment", "uppercase", "lowercase", "titlecase"])


class UnicodeData:
    """Class for encapsulating the data in UnicodeData.txt"""

    def __init__(self):
        """Initialize the class by building the Unicode character database."""
        self._unicode_character_database = {}
        self._build_unicode_character_database()

    def _build_unicode_character_database(self):
        """
        Function for parsing the Unicode character data from the Unicode Character
        Database (UCD) and generating a lookup table.  For more info on the UCD,
        see the following website: https://www.unicode.org/ucd/
        """
        filename = "UnicodeData.txt"
        current_dir = os.path.abspath(os.path.dirname(__file__))
        tag = re.compile(r"<\w+?>")
        with open(os.path.join(current_dir, filename), "rb") as fp:
            for line in fp:
                if not line.strip():
                    continue
                data = line.strip().split(";")
                data[0] = _hexstr_to_unichr(data[0])  # code
                data[3] = int(data[3])  # Convert the Canonical Combining Class value into an int.
                if data[5]:  # Convert the contents of the decomposition into characters, preserving tag info.
                    data[5] = u" ".join([_hexstr_to_unichr(s) if not tag.match(s) else s for s in data[5].split()])
                for i in [6, 7, 8]:  # Convert the decimal, digit and numeric fields to either ints or fractions.
                    if data[i]:
                        if "/" in data[i]:
                            data[i] = Fraction(data[i])
                        else:
                            data[i] = int(data[i])
                for i in [12, 13, 14]:  # Convert the uppercase, lowercase and titlecase fields to characters.
                    if data[i]:
                        data[i] = _hexstr_to_unichr(data[i])
                self._unicode_character_database[data[0]] = UnicodeCharacter(*data[1:])

    def get(self, c):
        """
        Function for retrieving the UnicodeCharacter associated with the character c.

        :param c: Character to look up.
        :return: UnicodeCharacter instance with data associated with the character.
        """
        return self._unicode_character_database[c]

    def __getitem__(self, item):
        """
        Function for retrieving the UnicodeCharacter associated with the character c.

        :param item: Character to look up.
        :return: UnicodeCharacter instance with data associated with the character.
        """
        return self._unicode_character_database.__getitem__(item)

    def __iter__(self):
        """Function for iterating through the keys of the data."""
        return self._unicode_character_database.__iter__()

    def items(self):
        """
        Returns a list of the data's (key, value) pairs, as tuples.

        :return: list of (key, value) pairs, as tuples.
        """
        return self._unicode_character_database.items()

    def keys(self):
        """
        Returns a list of the data's keys.

        :return: list of the data's keys
        """
        return self._unicode_character_database.keys()

    def values(self):
        """
        Returns a list of the data's values.

        :return:
        """
        return self._unicode_character_database.values()

    def name(self, name):
        """
        Function for retrieving the UnicodeCharacter associated with a name e.g.

        ucd = UnicodeData()
        ucd.name("LATIN SMALL LETTER SHARP S") -> UnicodeCharacter(name='LATIN SMALL LETTER SHARP S', category=..)

        :param name: Name of the character to look up.
        :return: UnicodeCharacter instance with data associated with the character.
        """
        # TODO: Implement this
        raise NotImplementedError("Not yet implemented!")


class CaseFoldingMap:
    """Class for performing Unicode case folding."""

    def __init__(self):
        """Initialize the class by building the casefold map."""
        self._build_casefold_map()

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
                src = _hexstr_to_unichr(code)
                target = u"".join([_hexstr_to_unichr(c) for c in mapping.strip().split()])
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
            raise TypeError(u"Character to lookup must be of type 'unicode'!")
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
    :param fullcasefold: Boolean indicating if a full case fold (default is True) should be done.  If False, a simple
                         case fold will be performed.
    :return: Copy of string that has been transformed for caseless comparison.
    """
    if not isinstance(s, unicode):
        raise TypeError(u"String to casefold must be of type 'unicode'!")
    lookup_order = "CF"
    if not fullcasefold:
        lookup_order = "CS"
    return u"".join([casefold_map.lookup(c, lookup_order=lookup_order) for c in preservesurrogates(s)])

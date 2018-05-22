from collections import defaultdict, namedtuple, OrderedDict
from fractions import Fraction
import codecs
import os
import re
import struct

import six

try:  # Python 2 style import
    from hangulutil import _get_hangul_syllable_name
except ImportError:  # Python 3 style import
    from .hangulutil import _get_hangul_syllable_name


#: Ranges of surrogate pairs
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
    if not isinstance(s, six.text_type):
        raise TypeError(u"String to split must be of type 'unicode'!")
    surrogates_regex_str = u"[{0}-{1}][{2}-{3}]".format(HIGH_SURROGATE_START,
                                                        HIGH_SURROGATE_END,
                                                        LOW_SURROGATE_START,
                                                        LOW_SURROGATE_END)
    surrogates_regex = re.compile(u"(?:{0})|.".format(surrogates_regex_str))
    return surrogates_regex.findall(s)


def _unichr(i):
    """
    Helper function for taking a Unicode scalar value and returning a Unicode character.

    :param s: Unicode scalar value to convert.
    :return: Unicode character
    """
    if not isinstance(i, int):
        raise TypeError
    try:
        return six.unichr(i)
    except ValueError:
        # Workaround the error "ValueError: unichr() arg not in range(0x10000) (narrow Python build)"
        return struct.pack("i", i).decode("utf-32")


def _hexstr_to_unichr(s):
    """
    Helper function for taking a hex string and returning a Unicode character.

    :param s: hex string to convert
    :return: Unicode character
    """
    return _unichr(int(s, 16))


def _padded_hex(i, pad_width=4, uppercase=True):
    """
    Helper function for taking an integer and returning a hex string.  The string will be padded on the left with zeroes
    until the string is of the specified width.  For example:

    _padded_hex(31, pad_width=4, uppercase=True) -> "001F"

    :param i: integer to convert to a hex string
    :param pad_width: (int specifying the minimum width of the output string.  String will be padded on the left with '0'
                      as needed.
    :param uppercase: Boolean indicating if we should use uppercase characters in the output string (default=True).
    :return: Hex string representation of the input integer.
    """
    result = hex(i)[2:]  # Remove the leading "0x"
    if uppercase:
        result = result.upper()
    return result.zfill(pad_width)


def _uax44lm2transform(s):
    """
    Helper function for taking a string (i.e. a Unicode character name) and transforming it via UAX44-LM2 loose matching
    rule.  For more information, see <https://www.unicode.org/reports/tr44/#UAX44-LM2>.

    The rule is defined as follows:

    "UAX44-LM2. Ignore case, whitespace, underscore ('_'), and all medial hyphens except the hyphen in
    U+1180 HANGUL JUNGSEONG O-E."

    Therefore, correctly implementing the rule involves performing the following three operations, in order:

    1. remove all medial hyphens (except the medial hyphen in the name for U+1180)
    2. remove all whitespace and underscore characters
    3. apply toLowercase() to both strings

    A "medial hyphen" is defined as follows (quoted from the above referenced web page):

    "In this rule 'medial hyphen' is to be construed as a hyphen occurring immediately between two letters in the
    normative Unicode character name, as published in the Unicode names list, and not to any hyphen that may transiently
    occur medially as a result of removing whitespace before removing hyphens in a particular implementation of
    matching. Thus the hyphen in the name U+10089 LINEAR B IDEOGRAM B107M HE-GOAT is medial, and should be ignored in
    loose matching, but the hyphen in the name U+0F39 TIBETAN MARK TSA -PHRU is not medial, and should not be ignored in
    loose matching."


    :param s: String to transform
    :return: String transformed per UAX44-LM2 loose matching rule.
    """
    result = s

    # For the regex, we are using lookaround assertions to verify that there is a word character immediately before (the
    # lookbehind assertion (?<=\w)) and immediately after (the lookahead assertion (?=\w)) the hyphen, per the "medial
    # hyphen" definition that it is a hyphen occurring immediately between two letters.
    medialhyphen = re.compile(r"(?<=\w)-(?=\w)")
    whitespaceunderscore = re.compile(r"[\s_]", re.UNICODE)

    # Ok to hard code, this name should never change: https://www.unicode.org/policies/stability_policy.html#Name
    if result != "HANGUL JUNGSEONG O-E":
        result = medialhyphen.sub("", result)
    result = whitespaceunderscore.sub("", result)
    return result.lower()


def _to_unicode_scalar_value(s):
    """
    Helper function for converting a character or surrogate pair into a Unicode scalar value e.g.
    "\ud800\udc00" -> 0x10000

    The algorithm can be found in older versions of the Unicode Standard.

    https://unicode.org/versions/Unicode3.0.0/ch03.pdf, Section 3.7, D28

    Unicode scalar value: a number N from 0 to 0x10FFFF is defined by applying the following algorithm to a
    character sequence S:
    If S is a single, non-surrogate value U:
    N = U
    If S is a surrogate pair H, L:
    N = (H - 0xD800) * 0x0400 + (L - 0xDC00) + 0x10000

    :param s:
    :return:
    """
    if len(s) == 1:
        return ord(s)
    elif len(s) == 2:
        return (ord(s[0]) - 0xD800) * 0x0400 + (ord(s[1]) - 0xDC00) + 0x10000
    else:
        raise ValueError


#: Dictionary for looking up the prefixes for derived names.
#: See Unicode Standard section 4.8 and table 4-8 for more information on the name derivation rules NR1 and NR2.
#: https://www.unicode.org/versions/Unicode10.0.0/ch04.pdf
_nr_prefix_strings = {
    six.moves.range( 0xAC00,  0xD7A3 + 1): "HANGUL SYLLABLE ",
    six.moves.range( 0x3400,  0x4DB5 + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range( 0x4E00,  0x9FEA + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range(0x20000, 0x2A6D6 + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range(0x2A700, 0x2B734 + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range(0x2B740, 0x2B81D + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range(0x2B820, 0x2CEA1 + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range(0x2CEB0, 0x2EBE0 + 1): "CJK UNIFIED IDEOGRAPH-",
    six.moves.range(0x17000, 0x187EC + 1): "TANGUT IDEOGRAPH-",
    six.moves.range(0x1B170, 0x1B2FB + 1): "NUSHU CHARACTER-",
    six.moves.range( 0xF900,  0xFA6D + 1): "CJK COMPATIBILITY IDEOGRAPH-",
    six.moves.range( 0xFA70,  0xFAD9 + 1): "CJK COMPATIBILITY IDEOGRAPH-",
    six.moves.range(0x2F800, 0x2FA1D + 1): "CJK COMPATIBILITY IDEOGRAPH-"
}


def _is_derived(i):
    """
    Helper function for determining if a Unicode scalar value falls into one of the ranges of derived names.

    :param i: Unicode scalar value.
    :return: Boolean.  True if the value is in one of the derived ranges.  False otherwise.
    """
    for lookup_range in _nr_prefix_strings.keys():
        if i in lookup_range:
            return True
    return False


def _get_nr_prefix(i):
    """
    Helper function for looking up the derived name prefix associated with a Unicode scalar value.

    :param i: Unicode scalar value.
    :return: String with the derived name prefix.
    """
    for lookup_range, prefix_string in _nr_prefix_strings.items():
        if i in lookup_range:
            return prefix_string
    raise ValueError("No prefix string associated with {0}!".format(i))


#: Documentation on the fields of UnicodeData.txt:
#: https://www.unicode.org/L2/L1999/UnicodeData.html
#: https://www.unicode.org/reports/tr44/#UnicodeData.txt
UnicodeCharacter = namedtuple("UnicodeCharacter", ["code", "name", "category", "combining", "bidi", "decomposition",
                                                   "decimal", "digit", "numeric", "mirrored", "unicode_1_name",
                                                   "iso_comment", "uppercase", "lowercase", "titlecase"])


class UnicodeData:
    """Class for encapsulating the data in UnicodeData.txt"""

    def __init__(self):
        """Initialize the class by building the Unicode character database."""
        self._unicode_character_database = {}
        self._name_database = {}
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
        with codecs.open(os.path.join(current_dir, filename), mode="r", encoding="utf-8") as fp:
            for line in fp:
                if not line.strip():
                    continue
                data = line.strip().split(";")
                # Replace the start/end range markers with their proper derived names.
                if data[1].endswith((u"First>", u"Last>")) and _is_derived(int(data[0], 16)):
                    data[1] = _get_nr_prefix(int(data[0], 16))
                    if data[1].startswith("HANGUL SYLLABLE"):  # For Hangul syllables, use naming rule NR1
                        data[1] += _get_hangul_syllable_name(int(data[0], 16))
                    else:  # Others should use naming rule NR2
                        data[1] += data[0]
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
                lookup_name = _uax44lm2transform(data[1])
                uc_data = UnicodeCharacter(u"U+" + data[0], *data[1:])
                self._unicode_character_database[int(data[0], 16)] = uc_data
                self._name_database[lookup_name] = uc_data
        # Fill out the "compressed" ranges of UnicodeData.txt i.e. fill out the remaining characters per the Name
        # Derivation Rules.  See the Unicode Standard, ch. 4, section 4.8, Unicode Name Property
        for lookup_range, prefix_string in _nr_prefix_strings.items():
            exemplar = self._unicode_character_database.__getitem__(lookup_range[0])
            for item in lookup_range:
                hex_code = _padded_hex(item)
                new_name = prefix_string
                if prefix_string.startswith("HANGUL SYLLABLE"):  # For Hangul, use naming rule NR1
                    new_name += _get_hangul_syllable_name(item)
                else:  # Everything else uses naming rule NR2
                    new_name += hex_code
                uc_data = exemplar._replace(code=u"U+" + hex_code, name=new_name)
                self._unicode_character_database[item] = uc_data
                self._name_database[_uax44lm2transform(new_name)] = uc_data

    def get(self, value):
        """
        Function for retrieving the UnicodeCharacter associated with the specified Unicode scalar value.

        :param value: Unicode scalar value to look up.
        :return: UnicodeCharacter instance with data associated with the specified value.
        """
        return self.__getitem__(value)

    def __getitem__(self, item):
        """
        Function for retrieving the UnicodeCharacter associated with the specified Unicode scalar value.

        :param item: Unicode scalar value to look up.
        :return: UnicodeCharacter instance with data associated with the specified value.
        """
        return self._unicode_character_database.__getitem__(item)

    def __iter__(self):
        """Function for iterating through the keys of the data."""
        return self._unicode_character_database.__iter__()

    def __len__(self):
        """Function for returning the size of the data."""
        return self._unicode_character_database.__len__()

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

        :return: list of the data's values.
        """
        return self._unicode_character_database.values()

    def lookup_by_char(self, c):
        """
        Function for retrieving the UnicodeCharacter associated with the specified Unicode character.

        :param c: Unicode character to look up.
        :return: UnicodeCharacter instance with data associated with the specified Unicode character.
        """
        return self._unicode_character_database[_to_unicode_scalar_value(c)]

    def lookup_by_name(self, name):
        """
        Function for retrieving the UnicodeCharacter associated with a name.  The name lookup uses the loose matching
        rule UAX44-LM2 for loose matching.  See the following for more info:

        https://www.unicode.org/reports/tr44/#UAX44-LM2

        For example:

        ucd = UnicodeData()
        ucd.lookup_by_name("LATIN SMALL LETTER SHARP S") -> UnicodeCharacter(name='LATIN SMALL LETTER SHARP S',...)
        ucd.lookup_by_name("latin_small_letter_sharp_s") -> UnicodeCharacter(name='LATIN SMALL LETTER SHARP S',...)


        :param name: Name of the character to look up.
        :return: UnicodeCharacter instance with data associated with the character.
        """
        try:
            return self._name_database[_uax44lm2transform(name)]
        except KeyError:
            raise KeyError(u"Unknown character name: '{0}'!".format(name))

    def lookup_by_partial_name(self, partial_name):
        """
        Similar to lookup_by_name(name), this method uses loose matching rule UAX44-LM2 to attempt to find the
        UnicodeCharacter associated with a name.  However, it attempts to permit even looser matching by doing a
        substring search instead of a simple match.  This method will return a generator that yields instances of
        UnicodeCharacter where the partial_name passed in is a substring of the full name.

        For example:

        >>> ucd = UnicodeData()
        >>> for data in ucd.lookup_by_partial_name("SHARP S"):
        >>>     print(data.code + " " + data.name)
        >>>
        >>> U+00DF LATIN SMALL LETTER SHARP S
        >>> U+1E9E LATIN CAPITAL LETTER SHARP S
        >>> U+266F MUSIC SHARP SIGN

        :param partial_name: Partial name of the character to look up.
        :return: Generator that yields instances of UnicodeCharacter.
        """
        for k, v in self._name_database.items():
            if _uax44lm2transform(partial_name) in k:
                yield v


class UnicodeBlocks:
    """Class for encapsulating the data in Blocks.txt"""

    def __init__(self):
        """Initialize the class by loading the Unicode block info."""
        self._unicode_blocks = OrderedDict()
        self._load_unicode_block_info()

    def _load_unicode_block_info(self):
        """
        Function for parsing the Unicode block info from the Unicode Character
        Database (UCD) and generating a lookup table.  For more info on the UCD,
        see the following website: https://www.unicode.org/ucd/
        """
        filename = "Blocks.txt"
        current_dir = os.path.abspath(os.path.dirname(__file__))
        with codecs.open(os.path.join(current_dir, filename), mode="r", encoding="utf-8") as fp:
            for line in fp:
                if not line.strip() or line.startswith("#"):
                    continue  # Skip empty lines or lines that are comments (comments start with '#')
                # Format: Start Code..End Code; Block Name
                block_range, block_name = line.strip().split(";")
                start_range, end_range = block_range.strip().split("..")
                self._unicode_blocks[six.moves.range(int(start_range, 16), int(end_range, 16) + 1)] = block_name.strip()

    def get(self, value):
        """
        Function for retrieving the Unicode Block name associated with the specified Unicode scalar value.

        :param value: Unicode scalar value to look up.
        :return: Unicode Block name associated with the specified value.
        """
        return self.__getitem__(value)

    def __getitem__(self, item):
        """
        Function for retrieving the Unicode Block name associated with the specified Unicode scalar value.

        :param item: Unicode scalar value to look up.
        :return: Unicode Block name associated with the specified value.
        """
        for block_range, name in self._unicode_blocks.items():
            if item in block_range:
                return name
        return u"No_Block"

    def items(self):
        """
        Returns a list of the data's (key, value) pairs, as tuples.

        :return: list of (key, value) pairs, as tuples.
        """
        return self._unicode_blocks.items()

    def keys(self):
        """
        Returns a list of the data's keys.

        :return: list of the data's keys
        """
        return self._unicode_blocks.keys()

    def values(self):
        """
        Returns a list of the data's values.

        :return: list of the data's values.
        """
        return self._unicode_blocks.values()

    def lookup_by_char(self, c):
        """
        Function for retrieving the Unicode Block name associated with the specified Unicode character.

        :param c: Unicode character to look up.
        :return: Unicode Block name associated with the specified Unicode character.
        """
        return self.__getitem__(_to_unicode_scalar_value(c))


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
        with codecs.open(os.path.join(current_dir, filename), mode="r", encoding="utf-8") as fp:
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
        if not isinstance(c, six.text_type):
            raise TypeError(u"Character to lookup must be of type 'unicode'!")
        for d in lookup_order:
            try:
                return self._casefold_map[d][c]
            except KeyError:
                pass
        return c


casefold_map = CaseFoldingMap()


def casefold(s, fullcasefold=True, useturkicmapping=False):
    """
    Function for performing case folding.  This function will take the input
    string s and return a copy of the string suitable for caseless comparisons.
    The input string must be of type 'unicode', otherwise a TypeError will be
    raised.

    For more information on case folding, see section 3.13 of the Unicode Standard.
    See also the following FAQ on the Unicode website:

    https://unicode.org/faq/casemap_charprop.htm

    By default, full case folding (where the string length may change) is done.
    It is possible to use simple case folding (single character mappings only)
    by setting the boolean parameter fullcasefold=False.

    By default, case folding does not handle the Turkic case of dotted vs dotless 'i'.
    To perform case folding using the special Turkic mappings, pass the boolean
    parameter useturkicmapping=True.  For more info on the dotted vs dotless 'i', see
    the following web pages:

    https://en.wikipedia.org/wiki/Dotted_and_dotless_I
    http://www.i18nguy.com/unicode/turkish-i18n.html#problem

    :param s: String to transform
    :param fullcasefold: Boolean indicating if a full case fold (default is True) should be done.  If False, a simple
                         case fold will be performed.
    :param useturkicmapping: Boolean indicating if the special turkic mapping (default is False) for the dotted and
                             dotless 'i' should be used.
    :return: Copy of string that has been transformed for caseless comparison.
    """
    if not isinstance(s, six.text_type):
        raise TypeError(u"String to casefold must be of type 'unicode'!")
    lookup_order = "CF"
    if not fullcasefold:
        lookup_order = "CS"
    if useturkicmapping:
        lookup_order = "T" + lookup_order
    return u"".join([casefold_map.lookup(c, lookup_order=lookup_order) for c in preservesurrogates(s)])

import codecs
import os
import six


_hangul_syllable_types = {}
_jamo_short_names = {}


def _load_hangul_syllable_types():
    """
    Helper function for parsing the contents of "HangulSyllableType.txt" from the Unicode Character Database (UCD) and
    generating a lookup table for determining whether or not a given Hangul syllable is of type "L", "V", "T", "LV" or
    "LVT".  For more info on the UCD, see the following website: https://www.unicode.org/ucd/
    """
    filename = "HangulSyllableType.txt"
    current_dir = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(current_dir, filename), mode="r", encoding="utf-8") as fp:
        for line in fp:
            if not line.strip() or line.startswith("#"):
                continue  # Skip empty lines or lines that are comments (comments start with '#')
            data = line.strip().split(";")
            syllable_type, _ = map(six.text_type.strip, data[1].split("#"))
            if ".." in data[0]:  # If it is a range and not a single value
                start, end = map(lambda x: int(x, 16), data[0].strip().split(".."))
                for idx in range(start, end + 1):
                    _hangul_syllable_types[idx] = syllable_type
            else:
                _hangul_syllable_types[int(data[0].strip(), 16)] = syllable_type


def _load_jamo_short_names():
    """
    Function for parsing the Jamo short names from the Unicode Character Database (UCD) and generating a lookup table
    For more info on how this is used, see the Unicode Standard, ch. 03, section 3.12, "Conjoining Jamo Behavior" and
    ch. 04, section 4.8, "Name".

    https://www.unicode.org/versions/latest/ch03.pdf
    https://www.unicode.org/versions/latest/ch04.pdf
    """
    filename = "Jamo.txt"
    current_dir = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(current_dir, filename), mode="r", encoding="utf-8") as fp:
        for line in fp:
            if not line.strip() or line.startswith("#"):
                continue  # Skip empty lines or lines that are comments (comments start with '#')
            data = line.strip().split(";")
            code = int(data[0].strip(), 16)
            char_info = data[1].split("#")
            short_name = char_info[0].strip()
            _jamo_short_names[code] = short_name


def _is_hangul_syllable(i):
    """
    Function for determining if a Unicode scalar value i is within the range of Hangul syllables.

    :param i: Unicode scalar value to lookup
    :return: Boolean: True if the lookup value is within the range of Hangul syllables, otherwise False.
    """
    if i in range(0xAC00, 0xD7A3 + 1):  # Range of Hangul characters as defined in UnicodeData.txt
        return True
    return False


def _is_jamo(i):
    """
    Function for determining if a Unicode scalar value i is within the range of Jamo.

    :param i: Unicode scalar value to lookup
    :return: Boolean: True if the lookup value is within the range of Hangul syllables, otherwise False.
    """
    if i in range(0x1100, 0x11ff + 1):  # Range of Jamo as defined in Blocks.txt, "1100..11FF; Hangul Jamo"
        return True
    return False


def _get_hangul_syllable_type(hangul_syllable):
    """
    Function for taking a Unicode scalar value representing a Hangul syllable and determining the correct value for its
    Hangul_Syllable_Type property.  For more information on the Hangul_Syllable_Type property see the Unicode Standard,
    ch. 03, section 3.12, Conjoining Jamo Behavior.

    https://www.unicode.org/versions/latest/ch03.pdf

    :param hangul_syllable: Unicode scalar value representing a Hangul syllable
    :return: Returns a string representing its Hangul_Syllable_Type property ("L", "V", "T", "LV" or "LVT")
    """
    if not _is_hangul_syllable(hangul_syllable):
        raise ValueError("Value 0x%0.4x does not represent a Hangul syllable!" % hangul_syllable)
    if not _hangul_syllable_types:
        _load_hangul_syllable_types()
    return _hangul_syllable_types[hangul_syllable]


def _get_jamo_short_name(jamo):
    """
    Function for taking a Unicode scalar value representing a Jamo and determining the correct value for its
    Jamo_Short_Name property.  For more information on the Jamo_Short_Name property see the Unicode Standard,
    ch. 03, section 3.12, Conjoining Jamo Behavior.

    https://www.unicode.org/versions/latest/ch03.pdf

    :param jamo: Unicode scalar value representing a Jamo
    :return: Returns a string representing its Jamo_Short_Name property
    """
    if not _is_jamo(jamo):
        raise ValueError("Value 0x%0.4x passed in does not represent a Jamo!" % jamo)
    if not _jamo_short_names:
        _load_jamo_short_names()
    return _jamo_short_names[jamo]


#: Common constants for decomposing and composing Hangul syllables
S_BASE = 0xAC00  # U+AC00, start of Hangul syllable range
L_BASE = 0x1100  # U+1100, start of Hangul leading consonant / syllable-initial range i.e. Hangul Choseong
V_BASE = 0x1161  # U+1161, start of Hangul vowel / syllable-peak range i.e Hangul Jungseong
T_BASE = 0x11a7  # U+11A7, start of Hangul trailing consonant / syllable-final range i.e. Hangul Jongseong
L_COUNT = 19  # Count of Hangul Choseong
V_COUNT = 21  # Count of Hangul Jungseong
T_COUNT = 28  # Count of Hangul Jongseong + 1
N_COUNT = V_COUNT * T_COUNT
S_COUNT = L_COUNT * N_COUNT


def compose_hangul_syllable(jamo):
    """
    Function for taking a tuple or list of Unicode scalar values representing Jamo and composing it into a Hangul
    syllable.  If the values in the list or tuple passed in are not in the ranges of Jamo, a ValueError will be raised.

    The algorithm for doing the composition is described in the Unicode Standard, ch. 03, section 3.12, "Conjoining Jamo
    Behavior."

    Example: (U+1111, U+1171) -> U+D4CC
             (U+D4CC, U+11B6) -> U+D4DB
             (U+1111, U+1171, U+11B6) -> U+D4DB

    :param jamo: Tuple of list of Jamo to compose
    :return: Composed Hangul syllable
    """
    fmt_str_invalid_sequence = "{0} does not represent a valid sequence of Jamo!"
    if len(jamo) == 3:
        l_part, v_part, t_part = jamo
        if not (l_part in range(0x1100, 0x1112 + 1) and
                v_part in range(0x1161, 0x1175 + 1) and
                t_part in range(0x11a8, 0x11c2 + 1)):
            raise ValueError(fmt_str_invalid_sequence.format(jamo))
        l_index = l_part - L_BASE
        v_index = v_part - V_BASE
        t_index = t_part - T_BASE
        lv_index = l_index * N_COUNT + v_index * T_COUNT
        return S_BASE + lv_index + t_index
    elif len(jamo) == 2:
        if jamo[0] in range(0x1100, 0x1112 + 1) and jamo[1] in range(0x1161, 0x1175 + 1):
            l_part, v_part = jamo
            l_index = l_part - L_BASE
            v_index = v_part - V_BASE
            lv_index = l_index * N_COUNT + v_index * T_COUNT
            return S_BASE + lv_index
        elif _get_hangul_syllable_type(jamo[0]) == "LV" and jamo[1] in range(0x11a8, 0x11c2 + 1):
            lv_part, t_part = jamo
            t_index = t_part - T_BASE
            return lv_part + t_index
        else:
            raise ValueError(fmt_str_invalid_sequence.format(jamo))
    else:
        raise ValueError(fmt_str_invalid_sequence.format(jamo))


def decompose_hangul_syllable(hangul_syllable, fully_decompose=False):
    """
    Function for taking a Unicode scalar value representing a Hangul syllable and decomposing it into a tuple
    representing the scalar values of the decomposed (canonical decomposition) Jamo.  If the Unicode scalar value
    passed in is not in the range of Hangul syllable values (as defined in UnicodeData.txt), a ValueError will be
    raised.

    The algorithm for doing the decomposition is described in the Unicode Standard, ch. 03, section 3.12,
    "Conjoining Jamo Behavior".

    Example: U+D4DB -> (U+D4CC, U+11B6)  # (canonical decomposition, default)
             U+D4DB -> (U+1111, U+1171, U+11B6)  # (full canonical decomposition)

    :param hangul_syllable: Unicode scalar value for Hangul syllable
    :param fully_decompose: Boolean indicating whether or not to do a canonical decomposition (default behavior is
                            fully_decompose=False) or a full canonical decomposition (fully_decompose=True)
    :return: Tuple of Unicode scalar values for the decomposed Jamo.
    """
    if not _is_hangul_syllable(hangul_syllable):
        raise ValueError("Value passed in does not represent a Hangul syllable!")
    s_index = hangul_syllable - S_BASE

    if fully_decompose:
        l_index = s_index // N_COUNT
        v_index = (s_index % N_COUNT) // T_COUNT
        t_index = s_index % T_COUNT
        l_part = L_BASE + l_index
        v_part = V_BASE + v_index
        t_part = (T_BASE + t_index) if t_index > 0 else None
        return l_part, v_part, t_part
    else:
        if _get_hangul_syllable_type(hangul_syllable) == "LV":  # Hangul_Syllable_Type = LV
            l_index = s_index // N_COUNT
            v_index = (s_index % N_COUNT) // T_COUNT
            l_part = L_BASE + l_index
            v_part = V_BASE + v_index
            return l_part, v_part
        else:  # Assume Hangul_Syllable_Type = LVT
            lv_index = (s_index // T_COUNT) * T_COUNT
            t_index = s_index % T_COUNT
            lv_part = S_BASE + lv_index
            t_part = T_BASE + t_index
            return lv_part, t_part


def _get_hangul_syllable_name(hangul_syllable):
    """
    Function for taking a Unicode scalar value representing a Hangul syllable and converting it to its syllable name as
    defined by the Unicode naming rule NR1.  See the Unicode Standard, ch. 04, section 4.8, Names, for more information.

    :param hangul_syllable: Unicode scalar value representing the Hangul syllable to convert
    :return: String representing its syllable name as transformed according to naming rule NR1.
    """
    if not _is_hangul_syllable(hangul_syllable):
        raise ValueError("Value passed in does not represent a Hangul syllable!")
    jamo = decompose_hangul_syllable(hangul_syllable, fully_decompose=True)
    result = ''
    for j in jamo:
        if j is not None:
            result += _get_jamo_short_name(j)
    return result

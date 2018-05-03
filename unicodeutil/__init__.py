try:
    from hangulutil import decompose_hangul_syllable
    from unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates  # Python 2 style import
except ImportError:
    from .hangulutil import decompose_hangul_syllable
    from .unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates  # Python 3 style import

UNIDATA_VERSION = "10.0.0"  # Version number of Unicode character data

__all__ = ["CaseFoldingMap", "UnicodeData", "casefold", "decompose_hangul_syllable", "preservesurrogates",
           "UNIDATA_VERSION"]

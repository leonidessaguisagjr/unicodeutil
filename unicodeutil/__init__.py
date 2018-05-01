try:
    from hangulutil import decompose_hangul_syllable
    from unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates  # Python 2 style import
except ImportError:
    from .hangulutil import decompose_hangul_syllable
    from .unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates  # Python 3 style import

__all__ = ["CaseFoldingMap", "UnicodeData", "casefold", "decompose_hangul_syllable", "preservesurrogates"]

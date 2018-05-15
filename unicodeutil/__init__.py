import pkg_resources

try:
    from hangulutil import compose_hangul_syllable, decompose_hangul_syllable
    from unicodeutil import CaseFoldingMap, UnicodeBlocks, UnicodeData, casefold, preservesurrogates  # Python 2 style import
except ImportError:
    from .hangulutil import compose_hangul_syllable, decompose_hangul_syllable
    from .unicodeutil import CaseFoldingMap, UnicodeBlocks, UnicodeData, casefold, preservesurrogates  # Python 3 style import

UNIDATA_VERSION = "10.0.0"  # Version number of Unicode character data

__all__ = ["CaseFoldingMap", "UnicodeBlocks", "UnicodeData", "casefold", "compose_hangul_syllable", "decompose_hangul_syllable",
           "preservesurrogates", "UNIDATA_VERSION"]

__version__ = pkg_resources.get_distribution('unicodeutil').version

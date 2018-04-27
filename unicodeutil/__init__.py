__all__ = ["unicodeutil"]

try:
    from unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates  # Python 2 style import
except ImportError:
    from .unicodeutil import CaseFoldingMap, UnicodeData, casefold, preservesurrogates  # Python 3 style import

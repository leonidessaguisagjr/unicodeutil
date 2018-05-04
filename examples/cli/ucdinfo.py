#!/usr/bin/env python

import argparse
import sys

import six

from unicodeutil import UnicodeData


def main():
    parser = argparse.ArgumentParser(
        description=
        u"A utility for displaying the information about a character from the Unicode\u00ae Character Database (UCD).")
    parser.add_argument(u"char",
                        help=u"The Unicode\u00ae character to lookup, in hex e.g. 'U+200C', '0x200C' or simply '200C'")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    if args.char:
        lookup = args.char
        if lookup.upper().startswith((u"U+", u"0X")):
            lookup = lookup[2:]
        ucd = UnicodeData()
        try:
            scalar_lookup = int(lookup, 16)
            char_info = ucd[scalar_lookup]
            try:
                char = six.unichr(scalar_lookup)
            except ValueError:
                char = (u"\\U%08x" % scalar_lookup).decode("unicode-escape")
            print(u"char: {0}".format(char))
            # Ok to access, _asdict() is a documented method.
            for k, v in char_info._asdict().items():
                print(u"{0}: {1}".format(k, v))
        except (KeyError, ValueError):
            print(u"Error! Unable to find character info for U+{0}".format(lookup))


if __name__ == "__main__":
    main()

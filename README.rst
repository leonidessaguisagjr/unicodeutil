``unicodeutil.py``
==================

Python classes and functions for working with Unicode data.


Case folding function for Python 2
----------------------------------

``casefold(s)`` is a function for performing case folding per section 3.13 of the `Unicode Standard <https://www.unicode.org/versions/latest/ch03.pdf>`_.  Also see the `W3C page on case folding <https://www.w3.org/International/wiki/Case_folding>`_ for more information on what case folding is.

Python 3.3 and newer has ``str.casefold()`` already built in.  This is my attempt at building a case folding function to use with Python 2 and as such has only been tested with Python 2.7.14.  It essentially parses the ``CaseFolding.txt`` file that is included in the `Unicode Character Database <https://www.unicode.org/ucd/>`_ to build a dictionary that is then used as a lookup table to create a copy of the input string that has been transformed to facilitate caseless comparisons.

A bit more information about how I put this together on my `blog <http://www.leonidessaguisagjr.name/?p=231>`_.

By default, the ``casefold(s)`` function performs full case folding.  To use simple case folding, pass the parameter ``fullcasefold=False`` (the default is ``fullcasefold=True``).  See the comments in ``CaseFolding.txt`` for an explanation of the difference between simple and full case folding.

Example usage
^^^^^^^^^^^^^

Using Python 2::

   >>> from unicodeutil import casefold
   >>> s1 = u"weiß"
   >>> s2 = u"WEISS"
   >>> casefold(s1) == casefold(s2)
   True


Splitting a Python 2 string into chars, preserving surrogate pairs
-------------------------------------------------------------------------

The ``preservesurrogates(s)`` function will split a string into a list of characters, preserving `surrogate pairs <https://www.unicode.org/glossary/#surrogate_pair>`_.

Example usage
^^^^^^^^^^^^^

Using Python 2::

   >>> from unicodeutil import preservesurrogates
   >>> s = u"ABC\U0001e900DeF\U000118a0gHıİ"
   >>> list(s)
   [u'A', u'B', u'C', u'\ud83a', u'\udd00', u'D', u'e', u'F', u'\ud806', u'\udca0', u'g', u'H', u'\u0131', u'\u0130']
   >>> for c in s:
   ...     print c
   ...
   A
   B
   C
   ???
   ???
   D
   e
   F
   ???
   ???
   g
   H
   ı
   İ
   >>> list(preservesurrogates(s))
   [u'A', u'B', u'C', u'\U0001e900', u'D', u'e', u'F', u'\U000118a0', u'g', u'H', u'\u0131', u'\u0130']
   >>> for c in preservesurrogates(s):
   ...     print(c)
   ...
   A
   B
   C
   𞤀
   D
   e
   F
   𑢠
   g
   H
   ı
   İ


License
-------

This is released under an MIT license.  See the ``LICENSE`` file in this repository for more information.

The included ``CaseFolding.txt`` file is part of the Unicode Character Database that is published by the Unicode Consortium.  Please consult the `Unicode® Terms of Use <https://www.unicode.org/copyright.html>`_ prior to use.

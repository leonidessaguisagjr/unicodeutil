``unicodeutil``
===============

Python classes and functions for working with Unicode® data.  This was initially built with Python 2 in mind but has also been tested with Python 3, PyPy and PyPy3.


Dependencies
------------

This package has the following external dependencies:

* `six <https://pythonhosted.org/six/>`_ - for Python 2 to 3 compatibility


Case folding function
---------------------

``casefold(s)`` is a function for performing case folding per section 3.13 of the `Unicode® Standard <https://www.unicode.org/versions/latest/ch03.pdf>`_.  Also see the `W3C page on case folding <https://www.w3.org/International/wiki/Case_folding>`_ for more information on what case folding is.

Python 3.3 and newer has ``str.casefold()`` already built in.  This is my attempt at building a case folding function to use with Python 2 and as such was initially only tested with Python 2.7.14.  It essentially parses the ``CaseFolding.txt`` file that is included in the `Unicode® Character Database <https://www.unicode.org/ucd/>`_ to build a dictionary that is then used as a lookup table to create a copy of the input string that has been transformed to facilitate caseless comparisons.

A bit more information about how I put this together on my `blog <http://www.leonidessaguisagjr.name/?p=231>`_.

By default, the ``casefold(s)`` function performs full case folding.  To use simple case folding, pass the parameter ``fullcasefold=False`` (the default is ``fullcasefold=True``).  See the comments in ``CaseFolding.txt`` for an explanation of the difference between simple and full case folding.

By default, the ``casefold(s)`` function will not use the Turkic special case mappings for dotted and dotless 'i'.  To use the Turkic mapping, pass the parameter ``useturkicmapping=True`` to the function.  See the following web pages for more information on the dotted vs dotless 'i':

* https://en.wikipedia.org/wiki/Dotted_and_dotless_I
* http://www.i18nguy.com/unicode/turkish-i18n.html#problem


Example usage
^^^^^^^^^^^^^

Using Python 2::

   >>> from unicodeutil import casefold
   >>> s1 = u"weiß"
   >>> s2 = u"WEISS"
   >>> casefold(s1) == casefold(s2)
   True
   >>> s1 = u"LİMANI"
   >>> s2 = u"limanı"
   >>> casefold(s1) == casefold(s2)
   False
   >>> casefold(s1, useturkicmapping=True) == casefold(s2, useturkicmapping=True)
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

Using the latest Unicode® Character Database (UCD)
--------------------------------------------------

As of Python 2.7.14, the `unicodedata <https://docs.python.org/2/library/unicodedata.html>`_ module is still using data from version 5.2.0 of the UCD.  The UCD is currently up to version 10.0.0.  The ``UnicodeCharacter`` namedtuple encapsulates the various properties associated with each Unicode® character, as explained in `Unicode Standard Annex #44, UnicodeData.txt <https://www.unicode.org/reports/tr44/#UnicodeData.txt>`_.  The ``UnicodeData`` class represents the contents of the UCD as parsed from the `latest UnicodeData.txt <ftp://ftp.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt>`_ found on the Unicode Consortium FTP site.  Once an instance of the ``UnicodeData`` class has been created, it is possible to do ``dict`` style lookups using the Unicode characters, or lookups by name using the ``lookup_by_name(name)`` method.  The name lookup uses the `UAX44-LM2 <https://www.unicode.org/reports/tr44/#UAX44-LM2>`_ loose matching rule when doing lookups.  Iterating through all of the data is also possible via ``items()``, ``keys()`` and ``values()`` methods.

Example usage
^^^^^^^^^^^^^

Using Python 2::

   >>> from unicodeutil import UnicodeData
   >>> ucd = UnicodeData()
   >>> ucd[u"ß"]
   UnicodeCharacter(code=u'U+00DF', name='LATIN SMALL LETTER SHARP S', category='Ll', combining=0, bidi='L', decomposition='', decimal='', digit='', numeric='', mirrored='N', unicode_1_name='', iso_comment='', uppercase='', lowercase='', titlecase='')
   >>> ucd[u"İ"].name
   'LATIN CAPITAL LETTER I WITH DOT ABOVE'
   >>> ucd.lookup_by_name("latin small letter sharp_s")
   UnicodeCharacter(code=u'U+00DF', name='LATIN SMALL LETTER SHARP S', category='Ll', combining=0, bidi='L', decomposition='', decimal='', digit='', numeric='', mirrored='N', unicode_1_name='', iso_comment='', uppercase='', lowercase='', titlecase='')

License
-------

This is released under an MIT license.  See the ``LICENSE`` file in this repository for more information.

The included ``CaseFolding.txt``, ``Jamo.txt`` and ``UnicodeData.txt`` files are part of the Unicode® Character Database that is published by Unicode, Inc.  Please consult the `Unicode® Terms of Use <https://www.unicode.org/copyright.html>`_ prior to use.

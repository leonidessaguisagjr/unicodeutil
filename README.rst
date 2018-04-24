``unicodeutil.py``
==================

Python function for working with Unicode data.


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


License
-------

This is released under an MIT license.  See the ``LICENSE`` file in this repository for more information.

The included ``CaseFolding.txt`` file is part of the Unicode Character Database that is published by the Unicode Consortium.  Please consult the `Unicode® Terms of Use <https://www.unicode.org/copyright.html>`_ prior to use.

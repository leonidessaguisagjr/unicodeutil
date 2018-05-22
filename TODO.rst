TODO
====

- Update example web app UI test cases to add tests for partial name lookup, browse by block
- Parse additional info about characters
  - East Asian Width - ``EastAsianWidth.txt``
  - Han info - ``Unihan.zip``

DONE
====

- Add ``UnicodeBlocks`` class to encapsulate ``Blocks.txt`` (0.1.dev8)
- Add ``__len__()`` to ``UnicodeData`` class. (0.1.dev9)
- Expand 'compressed' ranges in ``UnicodeData`` (so things like the iterator, name lookup in the compressed ranges and len will work correctly.) (0.1.dev9)

#######
History
#######


*******************
0.2.2 (12-03-2018)
*******************

New methods/functionality
=========================

* `search_sra()` allows full text search on SRA metadata.


*******************
0.2.0 (12-03-2018)
*******************

Renamed methods
===============

The following methods have been renamed
and the changes are not compatible with 0.1.0
release:

* `get_query()` -> `query()`.
* `sra_convert()` -> `sra_metadata()`.
* `get_table_counts()` -> `all_row_counts()`.


New methods/functionality
=========================

* `download_sradb_file()` makes fetching `SRAmetadb.sqlite` file easy; wget is no longer
  required.
* `ftp` protocol is now supported besides `fsp` and hence `aspera-client` is now optional.
  We however, strongly recommend `aspera-client` for faster downloads.

Bug fixes
=========
* Silenced `SettingWithCopyWarning` by excplicitly doing operations on a copy of
  the dataframe instead of the original.

Besides these, all methods now follow a `numpydoc` compatible documentation.


******************
0.1.0 (12-01-2018)
******************

* First release on PyPI.

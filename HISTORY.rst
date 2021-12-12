#######
History
#######

*******************
1.1.0 (12-12-2021)
*******************
* Fixed `gsm-to-gse` failure (`#128 <https://github.com/saketkc/pysradb/pull/128>`_)
* Fixed case sensitivity bug for ENA search (`#144 <https://github.com/saketkc/pysradb/pull/144>`_)
* Fixed publication date bug for search (`#146 <https://github.com/saketkc/pysradb/pull/146>`_)
* Added support for downloading data from GEO `pysradb dowload -g <GSE>` (`#129 <https://github.com/saketkc/pysradb/pull/129>`_)

*******************
1.0.1 (01-10-2021)
*******************
* Dropped Python 3.6 since pandas 1.2 is not supported

*******************
1.0.0 (01-09-2021)
*******************
* Retired ``metadb`` and ``SRAdb`` based search through CLI - everything defaults to ``SRAweb``
* ``SRAweb`` now supports `search <https://saket-choudhary.me/pysradb/quickstart.html#search>`_
* `N/A` is now replaced with `pd.NA`
* Two new fields in `--detailed`: `instrument_model` and `instrument_model_desc` `#75 <https://github.com/saketkc/pysradb/issues/75>`_
* Updated documentation

*******************
0.11.1 (09-18-2020)
*******************
* `library_layout` is now outputted in metadata #56
*  `-detailed` unifies columns for ENA fastq links instead of appending _x/_y #59
* bugfix for parsing namespace in xml outputs #65
* XML errors from NCBI are now handled more gracefully #69
* Documentation and dependency updates


*******************
0.11.0 (09-04-2020)
*******************
* `pysradb download` now supports multiple threads for paralle downloads
* `pysradb download` also supports ultra fast downloads of FASTQs from ENA using aspera-client



*******************
0.10.3 (03-26-2020)
*******************
* Added test cases for SRAweb
* API limit exceeding errors are automagically handled
* Bug fixes for GSE <=> SRR
* Bug fix for metadata - supports multiple SRPs

Contributors

* Dibya Gautam
* Marius van den Beek

*******************
0.10.2 (02-05-2020)
*******************

* Bug fix: Handle API-rate limit exceeding => Retries
* Enhancement: 'Alternatives' URLs are now part of `--detailed`

*******************
0.10.1 (02-04-2020)
*******************

* Bug fix: Handle Python3.6 for capture_output in subprocess.run

*******************
0.10.0 (01-31-2020)
*******************

* All the subcommands (srx-to-srr, srx-to-srs) will now print additional columns where the first two columns represent the relevant conversion
* Fixed a bug where for fetching entries with single efetch record

*******************
0.9.9 (01-15-2020)
*******************

* Major fix: some SRRs would go missing as the experiment dict was being created only once per SRR (See #15)
* Features: More detailed metadata by default in the SRAweb mode
* See notebook: https://colab.research.google.com/drive/1C60V-

******************
0.9.7 (01-20-2020)
******************

* Feature: instrument, run size and total spots are now printed in the metadata by default (SRAweb mode only)
* Issue: Fixed an issue with srapath failing on SRP. srapath is now run on individual SRRs.

******************
0.9.6 (07-20-2019)
******************

* Introduced `SRAweb` to perform queries over the web if the SQLite is missing or does not contain the relevant record.

******************
0.9.0 (02-27-2019)
******************

Others
======

* This release completely changes the command line interface replacing click with argparse (https://github.com/saketkc/pysradb/pull/3)
* Removed Python 2 comptaible stale code

*******************
0.8.0 (02-26-2019)
*******************

New methods/functionality
=========================
* `srr-to-gsm`: convert SRR to GSM
* SRAmetadb.sqlite.gz file is deleted by default after extraction
* When SRAmetadb is not found a confirmation is seeked before downloading
* Confirmation option before SRA downloads

Bugfix
======
* download() works with wget

Others
======

* `--out_dir` is now `out-dir`


*******************
0.7.1 (02-18-2019)
*******************

Important: Python2 is no longer supported.
Please consider moving to Python3.

Bugfix
======

* Included docs in the index whihch were missed
  out in the previous release


*******************
0.7.0 (02-08-2019)
*******************

New methods/functionality
=========================
* `gsm-to-srr`: convert GSM to SRR
* `gsm-to-srx`: convert GSM to SRX
* `gsm-to-gse`: convert GSM to GSE


Renamed methods
===============

The following commad line options have been renamed
and the changes are not compatible with 0.6.0
release:

* `sra-metadata` -> `metadata`.
* `sra-search` -> `search`.
* `srametadb` -> `metadb`.



*******************
0.6.0 (12-25-2018)
*******************

Bugfix
======

* Fixed bugs introduced in 0.5.0 with API changes where
  multiple redundant columns were output in `sra-metadata`


New methods/functionality
=========================
* `download` now allows piped inputs




*******************
0.5.0 (12-24-2018)
*******************

New methods/functionality
=========================
* Support for filtering by SRX Id for SRA downloads.
* `srr_to_srx`: Convert SRR to SRX/SRP
* `srp_to_srx`: Convert SRP to SRX
* Stripped down `sra-metadata` to give minimal information
* Added `--assay`, `--desc`, `--detailed` flag for `sra-metadata`
* Improved table printing on terminal


*******************
0.4.2 (12-16-2018)
*******************

Bugfix
======

* Fixed unicode error in tests for Python2


*******************
0.4.0 (12-12-2018)
*******************

New methods/functionality
=========================

* Added a new `BASEdb` class to handle common database connections
* Initial support for GEOmetadb through GEOdb class
* Initial support or a command line interface:
  - download      Download SRA project (SRPnnnn)
  - gse-metadata  Fetch metadata for GEO ID (GSEnnnn)
  - gse-to-gsm    Get GSM(s) for GSE
  - gsm-metadata  Fetch metadata for GSM ID (GSMnnnn)
  - sra-metadata  Fetch metadata for SRA project (SRPnnnn)
* Added three separate notebooks for SRAdb, GEOdb, CLI usage

*******************
0.3.0 (12-05-2018)
*******************

New methods/functionality
=========================

* `sample_attribute` and `experiment_attribute` are now included by default in the df returned by `sra_metadata()`
* `expand_sample_attribute_columns: expand metadata dataframe based on attributes in `sample_attribute` column
*  New methods to guess cell/tissue/strain: `guess_cell_type()`/`guess_tissue_type()`/`guess_strain_type()`
*  Improved README and usage instructions


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

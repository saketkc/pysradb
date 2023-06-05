# History

## 2.1.0 (2023-05-16)

-   Fix for [gse-to-srp]{.title-ref} returning unrequested GSEs ([#186
    \<https://github.com/saketkc/pysradb/issues/190\>]{.title-ref})
-   Fix for [download]{.title-ref} using [public_urls]{.title-ref}
-   Fix for [gsm-to-srx]{.title-ref} returning false positives ([#165
    \<https://github.com/saketkc/pysradb/issues/165\>]{.title-ref})
-   Fix for delimiter not being consistent when metadata is printed on
    terminal ([#147
    \<https://github.com/saketkc/pysradb/issues/147\>]{.title-ref})
-   ENA search is currently broken because of an API change

## 2.0.2 (2023-04-09)

-   Fix for [gse-to-srp]{.title-ref} to handle cases where a project is
    missing but SRXs are returned ([#186
    \<https://github.com/saketkc/pysradb/issues/186\>]{.title-ref})
-   Fix gse-to-gsm ([#187
    \<https://github.com/saketkc/pysradb/issues/187\>]{.title-ref})

## 2.0.1 (2023-03-18)

-   Fix for [pysradb download]{.title-ref} - using
    [public_url]{.title-ref}
-   Fix for SRX -\> SRR and related conversions ([#183
    \<https://github.com/saketkc/pysradb/pull/183\>]{.title-ref})

## 2.0.0 (2023-02-23)

-   BREAKING change: Overhaul of how urls and associated metadata are
    returned (not backward compatible); all column names are lower cased
    by default
-   Fix extra space in \"organism_taxid\" column
-   Added support for Experiment attributes ([#89
    \<https://github.com/saketkc/pysradb/issues/89#issuecomment-1439319532\>]{.title-ref})

## 1.4.2 (06-17-2022)

-   Fix ENA fastq fetching ([#163
    \<https://github.com/saketkc/pysradb/issues/163\>]{.title-ref})

## 1.4.1 (06-04-2022)

-   Fix for fetchin alternative URLs

## 1.4.0 (06-04-2022)

-   Added ability to fetch alternative URLs (GCP/AWS) for metadata
    ([#161
    \<https://github.com/saketkc/pysradb/issues/161\>]{.title-ref})
-   Fix for xmldict 0.13.0 no longer defaulting to OrderedDict ([#159
    \<https://github.com/saketkc/pysradb/pull/159\>]{.title-ref})
-   Fix for missing experiment model and description in metadata ([#160
    \<https://github.com/saketkc/pysradb/issues/160\>]{.title-ref})

## 1.3.0 (02-18-2022)

-   Add [study_title]{.title-ref} to [\--detailed]{.title-ref} flag
    ([#152](https://github.com/saketkc/pysradb/issues/152))
-   Fix [KeyError]{.title-ref} in [metadata]{.title-ref} where some new
    IDs do not have any metadata
    ([#151](https://github.com/saketkc/pysradb/issues/151))

## 1.2.0 (01-10-2022)

-   Do not exit if a qeury returns no hits ([#149
    \<https://github.com/saketkc/pysradb/pull/149\>]{.title-ref})

## 1.1.0 (12-12-2021)

-   Fixed [gsm-to-gse]{.title-ref} failure
    ([#128](https://github.com/saketkc/pysradb/pull/128))
-   Fixed case sensitivity bug for ENA search
    ([#144](https://github.com/saketkc/pysradb/pull/144))
-   Fixed publication date bug for search
    ([#146](https://github.com/saketkc/pysradb/pull/146))
-   Added support for downloading data from GEO [pysradb dowload -g
    \<GSE\>]{.title-ref}
    ([#129](https://github.com/saketkc/pysradb/pull/129))

## 1.0.1 (01-10-2021)

-   Dropped Python 3.6 since pandas 1.2 is not supported

## 1.0.0 (01-09-2021)

-   Retired `metadb` and `SRAdb` based search through CLI - everything
    defaults to `SRAweb`
-   `SRAweb` now supports
    [search](https://saket-choudhary.me/pysradb/quickstart.html#search)
-   [N/A]{.title-ref} is now replaced with [pd.NA]{.title-ref}
-   Two new fields in \`\--detailed\`: [instrument_model]{.title-ref}
    and [instrument_model_desc]{.title-ref}
    [#75](https://github.com/saketkc/pysradb/issues/75)
-   Updated documentation

## 0.11.1 (09-18-2020)

-   [library_layout]{.title-ref} is now outputted in metadata #56
-   [-detailed]{.title-ref} unifies columns for ENA fastq links instead
    of appending \_x/\_y #59
-   bugfix for parsing namespace in xml outputs #65
-   XML errors from NCBI are now handled more gracefully #69
-   Documentation and dependency updates

## 0.11.0 (09-04-2020)

-   [pysradb download]{.title-ref} now supports multiple threads for
    paralle downloads
-   [pysradb download]{.title-ref} also supports ultra fast downloads of
    FASTQs from ENA using aspera-client

## 0.10.3 (03-26-2020)

-   Added test cases for SRAweb
-   API limit exceeding errors are automagically handled
-   Bug fixes for GSE \<=\> SRR
-   Bug fix for metadata - supports multiple SRPs

Contributors

-   Dibya Gautam
-   Marius van den Beek

## 0.10.2 (02-05-2020)

-   Bug fix: Handle API-rate limit exceeding =\> Retries
-   Enhancement: \'Alternatives\' URLs are now part of
    [\--detailed]{.title-ref}

## 0.10.1 (02-04-2020)

-   Bug fix: Handle Python3.6 for capture_output in subprocess.run

## 0.10.0 (01-31-2020)

-   All the subcommands (srx-to-srr, srx-to-srs) will now print
    additional columns where the first two columns represent the
    relevant conversion
-   Fixed a bug where for fetching entries with single efetch record

## 0.9.9 (01-15-2020)

-   Major fix: some SRRs would go missing as the experiment dict was
    being created only once per SRR (See #15)
-   Features: More detailed metadata by default in the SRAweb mode
-   See notebook: <https://colab.research.google.com/drive/1C60V->

## 0.9.7 (01-20-2020)

-   Feature: instrument, run size and total spots are now printed in the
    metadata by default (SRAweb mode only)
-   Issue: Fixed an issue with srapath failing on SRP. srapath is now
    run on individual SRRs.

## 0.9.6 (07-20-2019)

-   Introduced [SRAweb]{.title-ref} to perform queries over the web if
    the SQLite is missing or does not contain the relevant record.

## 0.9.0 (02-27-2019)

### Others

-   This release completely changes the command line interface replacing
    click with argparse (<https://github.com/saketkc/pysradb/pull/3>)
-   Removed Python 2 comptaible stale code

## 0.8.0 (02-26-2019)

### New methods/functionality

-   \`srr-to-gsm\`: convert SRR to GSM
-   SRAmetadb.sqlite.gz file is deleted by default after extraction
-   When SRAmetadb is not found a confirmation is seeked before
    downloading
-   Confirmation option before SRA downloads

### Bugfix

-   download() works with wget

### Others

-   [\--out_dir]{.title-ref} is now [out-dir]{.title-ref}

## 0.7.1 (02-18-2019)

Important: Python2 is no longer supported. Please consider moving to
Python3.

### Bugfix

-   Included docs in the index whihch were missed out in the previous
    release

## 0.7.0 (02-08-2019)

### New methods/functionality

-   \`gsm-to-srr\`: convert GSM to SRR
-   \`gsm-to-srx\`: convert GSM to SRX
-   \`gsm-to-gse\`: convert GSM to GSE

### Renamed methods

The following commad line options have been renamed and the changes are
not compatible with 0.6.0 release:

-   [sra-metadata]{.title-ref} -\> [metadata]{.title-ref}.
-   [sra-search]{.title-ref} -\> [search]{.title-ref}.
-   [srametadb]{.title-ref} -\> [metadb]{.title-ref}.

## 0.6.0 (12-25-2018)

### Bugfix

-   Fixed bugs introduced in 0.5.0 with API changes where multiple
    redundant columns were output in [sra-metadata]{.title-ref}

### New methods/functionality

-   [download]{.title-ref} now allows piped inputs

## 0.5.0 (12-24-2018)

### New methods/functionality

-   Support for filtering by SRX Id for SRA downloads.
-   \`srr_to_srx\`: Convert SRR to SRX/SRP
-   \`srp_to_srx\`: Convert SRP to SRX
-   Stripped down [sra-metadata]{.title-ref} to give minimal information
-   Added [\--assay]{.title-ref}, [\--desc]{.title-ref},
    [\--detailed]{.title-ref} flag for [sra-metadata]{.title-ref}
-   Improved table printing on terminal

## 0.4.2 (12-16-2018)

### Bugfix

-   Fixed unicode error in tests for Python2

## 0.4.0 (12-12-2018)

### New methods/functionality

-   Added a new [BASEdb]{.title-ref} class to handle common database
    connections
-   Initial support for GEOmetadb through GEOdb class
-   Initial support or a command line interface:
    -   download Download SRA project (SRPnnnn)
    -   gse-metadata Fetch metadata for GEO ID (GSEnnnn)
    -   gse-to-gsm Get GSM(s) for GSE
    -   gsm-metadata Fetch metadata for GSM ID (GSMnnnn)
    -   sra-metadata Fetch metadata for SRA project (SRPnnnn)
-   Added three separate notebooks for SRAdb, GEOdb, CLI usage

## 0.3.0 (12-05-2018)

### New methods/functionality

-   [sample_attribute]{.title-ref} and
    [experiment_attribute]{.title-ref} are now included by default in
    the df returned by [sra_metadata()]{.title-ref}
-   [expand_sample_attribute_columns: expand metadata dataframe based on
    attributes in \`sample_attribute]{.title-ref} column
-   New methods to guess cell/tissue/strain:
    [guess_cell_type()]{.title-ref}/[guess_tissue_type()]{.title-ref}/[guess_strain_type()]{.title-ref}
-   Improved README and usage instructions

## 0.2.2 (12-03-2018)

### New methods/functionality

-   [search_sra()]{.title-ref} allows full text search on SRA metadata.

## 0.2.0 (12-03-2018)

### Renamed methods

The following methods have been renamed and the changes are not
compatible with 0.1.0 release:

-   [get_query()]{.title-ref} -\> [query()]{.title-ref}.
-   [sra_convert()]{.title-ref} -\> [sra_metadata()]{.title-ref}.
-   [get_table_counts()]{.title-ref} -\> [all_row_counts()]{.title-ref}.

### New methods/functionality

-   [download_sradb_file()]{.title-ref} makes fetching
    [SRAmetadb.sqlite]{.title-ref} file easy; wget is no longer
    required.
-   [ftp]{.title-ref} protocol is now supported besides
    [fsp]{.title-ref} and hence [aspera-client]{.title-ref} is now
    optional. We however, strongly recommend [aspera-client]{.title-ref}
    for faster downloads.

### Bug fixes

-   Silenced [SettingWithCopyWarning]{.title-ref} by excplicitly doing
    operations on a copy of the dataframe instead of the original.

Besides these, all methods now follow a [numpydoc]{.title-ref}
compatible documentation.

## 0.1.0 (12-01-2018)

-   First release on PyPI.

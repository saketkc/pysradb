.. _srxtosrr:

##########
srx-to-srr
##########

``srx-to-srr`` converts a SRA experiment accession (SRX) to corresponding
SRA run accession(s) (SRR).

=================
Usage and options
=================

::


    $ pysradb srx-to-srr -h

    Usage: pysradb srx-to-srr [OPTIONS] SRX_IDS...

      Get SRR for a SRX

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --desc         Should sample_attribute be included
      --detailed     Output additional columns: [sample_accession,
                     study_accession]
      --expand       Should sample_attribute be expanded
      --saveto TEXT  Save output to file
      -h, --help     Show this message and exit.


====================================================================
Convert SRA experiment accession (SRX) to SRA run accession(s) (SRR)
====================================================================

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding SRA run accessions of the form ``SRRnnnn``:

::

    $ pysradb srx-to-srr SRX2189156

    experiment_accession run_accession
    SRX2189156           SRR4293693

=========================
Getting sample attributes
=========================

Often, the most useful information is in the ``sample_attribute``
column of ``SRAmetadb``. For example, what cell` types do
different experiments correspond to? What treatments have been
applied to them? This can be listed by using the ``-desc``
tag. If you also need the sample and experiment accessions,
SRS and SRX respectively, please use ``--detailed`` tag.


::

    $ pysradb srx-to-srr --desc SRX2189156

    experiment_accession run_accession sample_attribute
    SRX2189156           SRR4293693    source_name: colorectal carcinoma cell line || tissue: colon || cell line: HCT116 || phenotype: colorectal carcinoma


But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srx-to-srr --detailed --desc SRX2189156

    experiment_accession run_accession sample_accession study_accession experiment_alias run_alias      sample_alias study_alias sample_attribute
    SRX2189156           SRR4293693    SRS1711882       SRP090415       GSM2327825       GSM2327825_r1  GSM2327825   GSE87328    source_name: colorectal carcinoma cell line || tissue: colon || cell line: HCT116 || phenotype: colorectal carcinoma


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srx-to-srr --detailed --desc --expand SRX2189156

    experiment_accession run_accession sample_accession study_accession experiment_alias run_alias      sample_alias study_alias cell_line phenotype             source_name                     tissue
    SRX2189156           SRR4293693    SRS1711882       SRP090415       GSM2327825       GSM2327825_r1  GSM2327825   GSE87328    hct116    colorectal carcinoma  colorectal carcinoma cell line  colon

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srx-to-srr --detailed --expand --saveto SRX2189156_metadata.tsv SRX2189156

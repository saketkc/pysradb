.. _srxtosrs:

##########
srx-to-srs
##########

``srx-to-srs`` converts a SRA experiment accession (SRX) to corresponding
SRA sample accession (SRS).

=================
Usage and options
=================

::

    $ pysradb srx-to-srs -h

    Usage: pysradb srx-to-srs [OPTIONS] SRX_IDS...

      Get SRS for a SRX

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [run_accession, study_accession]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


====================================================================
Convert SRA experiment accession (SRX) to SRA sample accession (SRS)
====================================================================

To convert a SRA experiment accession(s) of the form ``SRXnnnn`` to its corresponding
SRA sample accession of the form ``SRSmmmmm``:

::

    $ pysradb srx-to-srs SRS718880

    experiment_accession sample_accession
    SRX2189156           SRS1711882

=========================
Getting sample attributes
=========================

Often, the most useful information is in the ``sample_attribute``
column of ``SRAmetadb``. For example, what cell` types do
different experiments correspond to? What treatments have been
applied to them? This can be listed by using the ``-desc``
tag. Note however that, this will not however any accessions
related to the experiment or run. You will need the ``--detailed``
tag if you want the sample/run/experiment accessions.


::

    $ pysradb srx-to-srs --desc SRX2189156

    experiment_accession sample_accession sample_attribute
    SRX2189156           SRS1711882       source_name: colorectal carcinoma cell line || tissue: colon || cell line: HCT116 || phenotype: colorectal carcinoma

But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srx-to-srs --detailed --desc SRX2189156

    experiment_accession sample_accession run_accession study_accession experiment_alias sample_alias run_alias      study_alias sample_attribute
    SRX2189156           SRS1711882       SRR4293693    SRP090415       GSM2327825       GSM2327825   GSM2327825_r1  GSE87328    source_name: colorectal carcinoma cell line || tissue: colon || cell line: HCT116 || phenotype: colorectal carcinoma

==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srx-to-srs --detailed --desc --expand SRX2189156

    experiment_accession sample_accession run_accession study_accession experiment_alias sample_alias run_alias      study_alias cell_line phenotype             source_name                     tissue
    SRX2189156           SRS1711882       SRR4293693    SRP090415       GSM2327825       GSM2327825   GSM2327825_r1  GSE87328    hct116    colorectal carcinoma  colorectal carcinoma cell line  colon

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srx-to-srs --detailed --expand --saveto SRX2189156_metadata.tsv SRX2189156


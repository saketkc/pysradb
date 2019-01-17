.. _srstosrx:

##########
srs-to-srx
##########

``srs-to-srx`` converts a SRA sample accession (SRS) to corresponding
SRA experiment accession (SRX).

=================
Usage and options
=================

::

    $ pysradb srs-to-srx -h

    Usage: pysradb srs-to-srx [OPTIONS] SRS_IDS...

      Get SRX for a SRS

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [run_accession, study_accession]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


====================================================================
Convert SRA sample accession (SRS) to SRA experiment accession (SRX)
====================================================================

To convert a SRA sample accession of the form ``SRSmmmmm`` to its
corresponding SRA experiment accession(s) of the form ``SRXnnnn``:

::

    $ pysradb srs-to-srx SRS718880

    sample_accession experiment_accession
    SRS718880        SRX729554

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

    $ pysradb srs-to-srx --desc SRP098789

    sample_accession experiment_accession sample_attribute
    SRS718880        SRX729554            source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia

But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srs-to-srx --detailed --desc SRP098789

    sample_accession experiment_accession run_accession study_accession sample_alias experiment_alias run_alias      study_alias sample_attribute
    SRS718880        SRX729554            SRR1608498    SRP048759       GSM1521545   GSM1521545       GSM1521545_r1  GSE62190    source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRS718880        SRX729554            SRR1608499    SRP048759       GSM1521545   GSM1521545       GSM1521545_r2  GSE62190    source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRS718880        SRX729554            SRR1608500    SRP048759       GSM1521545   GSM1521545       GSM1521545_r3  GSE62190    source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRS718880        SRX729554            SRR1608501    SRP048759       GSM1521545   GSM1521545       GSM1521545_r4  GSE62190    source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia

==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srs-to-srx --detailed --desc --expand SRP098789

    sample_accession experiment_accession run_accession study_accession sample_alias experiment_alias run_alias      study_alias cell_type               source_name             tissue
    SRS718880        SRX729554            SRR1608498    SRP048759       GSM1521545   GSM1521545       GSM1521545_r1  GSE62190    acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRS718880        SRX729554            SRR1608499    SRP048759       GSM1521545   GSM1521545       GSM1521545_r2  GSE62190    acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRS718880        SRX729554            SRR1608500    SRP048759       GSM1521545   GSM1521545       GSM1521545_r3  GSE62190    acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRS718880        SRX729554            SRR1608501    SRP048759       GSM1521545   GSM1521545       GSM1521545_r4  GSE62190    acute myeloid leukemia  acute myeloid leukemia  heparinised blood

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srs-to-srx --detailed --expand --saveto SRP098789_metadata.tsv SRP098789

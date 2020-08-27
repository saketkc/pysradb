.. _srptosrs:

##########
srp-to-srs
##########

``srp-to-srs`` converts a SRA study accession (SRP) to corresponding
SRA sample accession(s) (SRS).

=================
Usage and options
=================

::


    Usage: pysradb srp-to-srs [OPTIONS] SRP_ID

      Get SRS for a SRP

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [run_accession (SRR),
                     study_accession (SRP),
                     experiment_alias (GSM),
                     sample_alias (GSM_),
                     run_alias (GSM_r),
                     study_alias (GSE)]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


===============================================================
Convert SRA study accession (SRP) to SRA sample accession (SRS)
===============================================================

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding SRA run accessions of the form ``SRRnnnn``:

::

    $ pysradb srp-to-srs SRP048759 | head

    study_accession sample_accession
    SRP048759       SRS718878
    SRP048759       SRS718879
    SRP048759       SRS718880
    SRP048759       SRS718881
    SRP048759       SRS718882
    SRP048759       SRS718883
    SRP048759       SRS718884
    SRP048759       SRS718885
    SRP048759       SRS718886


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

    $ pysradb srp-to-srs --desc SRP048759 | head

    study_accession sample_accession sample_attribute
    SRP048759       SRS718878        source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718879        source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718880        source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718881        source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718882        source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718883        source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718884        source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718885        source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718886        source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia



But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srp-to-srs --detailed --desc SRP048759 | head

    study_accession sample_accession experiment_accession run_accession study_alias sample_alias experiment_alias run_alias      sample_attribute
    SRP048759       SRS718878        SRX729552            SRR1608490    GSE62190    GSM1521543   GSM1521543       GSM1521543_r1  source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718878        SRX729552            SRR1608491    GSE62190    GSM1521543   GSM1521543       GSM1521543_r2  source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718878        SRX729552            SRR1608492    GSE62190    GSM1521543   GSM1521543       GSM1521543_r3  source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718878        SRX729552            SRR1608493    GSE62190    GSM1521543   GSM1521543       GSM1521543_r4  source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia
    SRP048759       SRS718879        SRX729553            SRR1608494    GSE62190    GSM1521544   GSM1521544       GSM1521544_r1  source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718879        SRX729553            SRR1608495    GSE62190    GSM1521544   GSM1521544       GSM1521544_r2  source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718879        SRX729553            SRR1608496    GSE62190    GSM1521544   GSM1521544       GSM1521544_r3  source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718879        SRX729553            SRR1608497    GSE62190    GSM1521544   GSM1521544       GSM1521544_r4  source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia
    SRP048759       SRS718880        SRX729554            SRR1608498    GSE62190    GSM1521545   GSM1521545       GSM1521545_r1  source_name: acute myeloid leukemia || tissue: Heparinised blood || cell type: acute myeloid leukemia

==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srp-to-srs --detailed --desc --expand SRP048759 | head

    study_accession sample_accession experiment_accession run_accession study_alias sample_alias experiment_alias run_alias      cell_type               source_name             tissue
    SRP048759       SRS718878        SRX729552            SRR1608490    GSE62190    GSM1521543   GSM1521543       GSM1521543_r1  acute myeloid leukemia  acute myeloid leukemia  bone marrow
    SRP048759       SRS718878        SRX729552            SRR1608491    GSE62190    GSM1521543   GSM1521543       GSM1521543_r2  acute myeloid leukemia  acute myeloid leukemia  bone marrow
    SRP048759       SRS718878        SRX729552            SRR1608492    GSE62190    GSM1521543   GSM1521543       GSM1521543_r3  acute myeloid leukemia  acute myeloid leukemia  bone marrow
    SRP048759       SRS718878        SRX729552            SRR1608493    GSE62190    GSM1521543   GSM1521543       GSM1521543_r4  acute myeloid leukemia  acute myeloid leukemia  bone marrow
    SRP048759       SRS718879        SRX729553            SRR1608494    GSE62190    GSM1521544   GSM1521544       GSM1521544_r1  acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRP048759       SRS718879        SRX729553            SRR1608495    GSE62190    GSM1521544   GSM1521544       GSM1521544_r2  acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRP048759       SRS718879        SRX729553            SRR1608496    GSE62190    GSM1521544   GSM1521544       GSM1521544_r3  acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRP048759       SRS718879        SRX729553            SRR1608497    GSE62190    GSM1521544   GSM1521544       GSM1521544_r4  acute myeloid leukemia  acute myeloid leukemia  heparinised blood
    SRP048759       SRS718880        SRX729554            SRR1608498    GSE62190    GSM1521545   GSM1521545       GSM1521545_r1  acute myeloid leukemia  acute myeloid leukemia  heparinised blood


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-srs --detailed --expand --saveto SRP048759_metadata.tsv SRP048759


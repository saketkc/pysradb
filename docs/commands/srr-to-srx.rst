.. _srrtosrx:

##########
srr-to-srx
##########

``srr-to-srx`` converts a SRA run accession (SRR) to corresponding
SRA sample accession (SRX).

Usage and options
=================

::

    $ pysradb srr-to-srx -h

    Usage: pysradb srr-to-srx [OPTIONS] SRR_IDS...

      Get SRX for a SRR

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --detailed     Output additional columns: [sample_accession (SRS),
                     study_accession (SRP),
                     run_alias (GSM_r),
                     experiment_alias
                     (GSM),
                     sample_alias (GSM_),
                     study_alias (GSE)]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      --saveto TEXT  Save output to file
      -h, --help     Show this message and exit.



==============================================================
Convert SRA run accession (SRR) to SRA sample accession (SRS)
==============================================================

To convert a SRA run accession of the form ``SRRmmmmm`` to its
corresponding SRA experiment accession of the form ``SRXnnnn``:

::

    $ pysradb srr-to-srx SRR1608490

    run_accession experiment_accession
    SRR1608490    SRX729552

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

    $ pysradb srr-to-srx --desc SRR1608490

    run_accession experiment_accession sample_attribute
    SRR1608490    SRX729552            source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia

But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srr-to-srx --detailed --desc SRR1608490

    run_accession experiment_accession sample_accession study_accession run_alias      experiment_alias sample_alias study_alias sample_attribute
    SRR1608490    SRX729552            SRS718878        SRP048759       GSM1521543_r1  GSM1521543       GSM1521543   GSE62190    source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia

==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srr-to-srx --detailed --desc --expand SRR1608490

    run_accession experiment_accession sample_accession study_accession run_alias      experiment_alias sample_alias study_alias cell_type               source_name             tissue
    SRR1608490    SRX729552            SRS718878        SRP048759       GSM1521543_r1  GSM1521543       GSM1521543   GSE62190    acute myeloid leukemia  acute myeloid leukemia  bone marrow

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srr-to-srx --detailed --expand --saveto SRR1608490_metadata.tsv SRR1608490


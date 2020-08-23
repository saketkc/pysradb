.. _srrtosrs:

##########
srr-to-srs
##########

``srr-to-srs`` converts a SRA run accession (SRR) to corresponding
SRA sample accession (SRS).

=================
Usage and options
=================

::

    $ pysradb srr-to-srs -h

    Usage: pysradb srr-to-srs [OPTIONS] SRR_IDS...

      Get SRS for a SRR

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --detailed     'Output additional columns: [experiment_accession (SRX),
                                                  study_accession (SRP),
                                                  run_alias (GSM_r),
                                                  sample_alias (GSM_),
                                                  experiment_alias (GSM),
                                                  study_alias (GSE)]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      --saveto TEXT  Save output to file
      -h, --help     Show this message and exit.


==============================================================
Convert SRA run accession (SRR) to SRA sample accession (SRS)
==============================================================

To convert a SRA run accession of the form ``SRRmmmmm`` to its
corresponding SRA sample accession of the form ``SRSnnnn``:

::

    $ pysradb srr-to-srs SRR1608490

    run_accession sample_accession
    SRR1608490    SRS718878

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

    $ pysradb srr-to-srs --desc SRR1608490

    run_accession sample_accession sample_attribute
    SRR1608490    SRS718878        source_name: acute myeloid leukemia || tissue: Bone marrow || cell type: acute myeloid leukemia


But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srr-to-srs --detailed --desc SRR1608490

    run_accession sample_accession cell_type               source_name             tissue
    SRR1608490    SRS718878        acute myeloid leukemia  acute myeloid leukemia  bone marrow


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srr-to-srs --detailed --desc --expand SRR1608490

    run_accession sample_accession experiment_accession study_accession run_alias      sample_alias experiment_alias study_alias cell_type               source_name             tissue
    SRR1608490    SRS718878        SRX729552            SRR1608490       GSM1521543_r1  GSM1521543   GSM1521543       GSE62190    acute myeloid leukemia  acute myeloid leukemia  bone marrow

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srr-to-srs --detailed --expand --saveto SRR1608490_metadata.tsv SRR1608490


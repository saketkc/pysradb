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
      --detailed     'Output additional columns: [experiment_accession (SRX),
                                                  study_accession (SRP),
                                                  run_alias (GSM_r),
                                                  sample_alias (GSM_),
                                                  experiment_alias (GSM),
                                                  study_alias (GSE)]
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

In order to obtain detailed metadata:

::

    $ pysradb srr-to-srs --detailed SRR1608490



=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srr-to-srs --detailed --saveto SRR1608490_metadata.tsv SRR1608490


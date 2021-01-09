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
      --detailed     Output additional columns: [sample_accession (SRS),
                     study_accession (SRP),
                     run_alias (GSM_r),
                     experiment_alias
                     (GSM),
                     sample_alias (GSM_),
                     study_alias (GSE)]
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

In order to obtain detailed metadata:

::

    $ pysradb srr-to-srx --detailed SRR1608490


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srr-to-srx --detailed --saveto SRR1608490_metadata.tsv SRR1608490


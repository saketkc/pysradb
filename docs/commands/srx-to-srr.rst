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
      --detailed     Output additional columns: [sample_accession,
                     study_accession]
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


In order to obtain detailed metadata:

::

    $ pysradb srx-to-srr --detailed SRX2189156

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srx-to-srr --detailed -saveto SRX2189156_metadata.tsv SRX2189156

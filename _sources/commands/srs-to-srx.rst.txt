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
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [run_accession, study_accession]
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

In order to obtain detailed metadata:

::

    $ pysradb srs-to-srx --detailed SRP098789


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srs-to-srx --detailed --saveto SRP098789_metadata.tsv SRP098789

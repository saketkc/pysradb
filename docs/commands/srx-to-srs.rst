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
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [run_accession, study_accession]
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

In order to obtain detailed metadata:

::

    $ pysradb srx-to-srs --detailed SRX2189156


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srx-to-srs --detailed --saveto SRX2189156_metadata.tsv SRX2189156


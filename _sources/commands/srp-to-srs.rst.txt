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
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [run_accession (SRR),
                     study_accession (SRP),
                     experiment_alias (GSM),
                     sample_alias (GSM_),
                     run_alias (GSM_r),
                     study_alias (GSE)]
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


In order to obtain detailed metadata:

::

    $ pysradb srp-to-srs --detailed SRP048759 | head


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-srs --detailed --saveto SRP048759_metadata.tsv SRP048759


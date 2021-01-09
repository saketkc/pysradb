.. _srptosrx:

##########
srp-to-srx
##########

``srp-to-srx`` converts a SRA study accession (SRP) to corresponding
SRA experiment accession(s) (SRX).

=================
Usage and options
=================

::

    $ pysradb srp-to-srx -h

    Usage: pysradb srp-to-srx [OPTIONS] SRP_ID

      Get SRX/SRR for a SRP

    Options:
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [sample_accession (SRS),
                     run_accession (SRR),
                     experiment_alias (GSM),
                     sample_alias
                     (GSM_),
                     run_alias (GSM_r)',
                     study_alias (GSE)]
      -h, --help     Show this message and exit.


===================================================================
Convert SRA study accession (SRP) to SRA experiment accession (SRX)
===================================================================

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding SRA experiment accession(s) of the form ``SRXnnnn``:

::

    $ pysradb srp-to-srx SRP098789

    experiment_accession study_accession
    SRX2536403           SRP098789
    SRX2536404           SRP098789
    SRX2536405           SRP098789
    SRX2536406           SRP098789
    SRX2536407           SRP098789
    SRX2536408           SRP098789
    SRX2536409           SRP098789
    SRX2536410           SRP098789
    SRX2536411           SRP098789
    SRX2536412           SRP098789
    SRX2536413           SRP098789
    SRX2536414           SRP098789
    SRX2536415           SRP098789
    SRX2536416           SRP098789
    SRX2536417           SRP098789
    SRX2536418           SRP098789
    SRX2536419           SRP098789
    SRX2536420           SRP098789
    SRX2536421           SRP098789
    SRX2536422           SRP098789
    SRX2536423           SRP098789
    SRX2536424           SRP098789
    SRX2536425           SRP098789
    SRX2536426           SRP098789
    SRX2536427           SRP098789
    SRX2536428           SRP098789

In order to obtain detailed metadata:

::

    $ pysradb srp-to-srx --detailed SRP098789

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-srx --detailed --saveto SRP098789_metadata.tsv SRP098789

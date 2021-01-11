.. _srptosrr:

##########
srp-to-srr
##########

``srp-to-srr`` converts a SRA study accession (SRP) to corresponding
SRA run accession(s) (SRR).

=================
Usage and options
=================

::


    $ pysradb srp-to-srr -h

    Usage: pysradb srp-to-srr [OPTIONS] SRP_ID

      Get SRR for a SRP

    Options:
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [experiment_accession (SRX),
                                                 sample_accession (SRS),
                                                 study_alias (GSE),
                                                 experiment_alias (GSM),
                                                 sample_alias (GSM_),
                                                 run_alias (GSM_r)],
      -h, --help     Show this message and exit.


===============================================================
Convert SRA study accession (SRP) to SRA run accession(s) (SRR)
===============================================================

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding SRA run accessions of the form ``SRRnnnn``:

::

    $ pysradb srp-to-srr SRP098789

    study_accession run_accession
    SRP098789       SRR5227288
    SRP098789       SRR5227289
    SRP098789       SRR5227290
    SRP098789       SRR5227291
    SRP098789       SRR5227292
    SRP098789       SRR5227293
    SRP098789       SRR5227294
    SRP098789       SRR5227295
    SRP098789       SRR5227296
    SRP098789       SRR5227297
    SRP098789       SRR5227298
    SRP098789       SRR5227299
    SRP098789       SRR5227300
    SRP098789       SRR5227301
    SRP098789       SRR5227302
    SRP098789       SRR5227303
    SRP098789       SRR5227304
    SRP098789       SRR5227305
    SRP098789       SRR5227306
    SRP098789       SRR5227307
    SRP098789       SRR5227308
    SRP098789       SRR5227309
    SRP098789       SRR5227310
    SRP098789       SRR5227311
    SRP098789       SRR5227312
    SRP098789       SRR5227313

In order to obtain detailed metadata:

::

    $ pysradb srp-to-srr --detailed SRP098789


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-srr --detailed SRP098789_metadata.tsv SRP098789


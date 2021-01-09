.. _gsetogsm:

##########
gse-to-gsm
##########

``gse-to-gsm`` provides list of GEO experiments (GSM) for a GEO study accession (GSE).

=================
Usage and options
=================

::


    $ pysradb gse-to-gsm

    Usage: pysradb gse-to-gsm [OPTIONS] GSE_IDS...

      Get SRP for a GSE

    Options:
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [sample_accession (SRS),
                                                 run_accession (SRR),
                                                 sample_alias (GSM),
                                                 run_alias (GSM_r)]
      -h, --help     Show this message and exit.



===============================================================
Convert GEO accession ID (GSE) to GEO expriment accession (GSM)
===============================================================

Getting GSMs from GSE is straight forward:

::

    $ pysradb gse-to-gsm GSE41637 | head

    study_alias experiment_alias
    GSE41637    GSM1020640_1
    GSE41637    GSM1020641_1
    GSE41637    GSM1020642_1
    GSE41637    GSM1020643_1
    GSE41637    GSM1020644_1
    GSE41637    GSM1020645_1
    GSE41637    GSM1020646_1
    GSE41637    GSM1020647_1
    GSE41637    GSM1020648_1



To get detailed output:

::

    $ pysradb gse-to-gsm --detailed GSE41637


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb gse-to-gsm --detailed --saveto GSE41637_metadata.tsv GSE41637


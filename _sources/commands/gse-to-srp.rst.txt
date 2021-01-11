.. _gsetosrp:

##########
gse-to-srp
##########

``gse-to-srp`` converts a GEO accession ID (GSE) to SRA
study accession (SRP).

=================
Usage and options
=================

::

    $ pysradb gse-to-srp -h

    Usage: pysradb gse-to-srp [OPTIONS] GSE_IDS...

      Get SRP for a GSE

    Options:
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [experiment_accession (SRX),
                                                 sample_accession (SRS),
                                                 experiment_alias (GSM_),
                                                 sample_alias (GSM)]
      -h, --help     Show this message and exit.


===========================================================
Convert GEO accession ID (GSE) to SRA study accession (SRP)
===========================================================

Gene Expression Omnibus or GEO hosts processed sequencing datasets.
The raw data is available through SRA and hence we often need to
interpolate between the two.

To convert a GEO experiment with ID of the form ``GSEnnnn`` to
its corresponding SRA study accession of the form ``SRPmmmmm``:

::

    $ pysradb gse-to-srp GSE41637

    study_alias study_accession
    GSE41637    SRP016501

=========================
Getting sample attributes
=========================

Often, the most useful information is in the expanded metadata.
For example, what cell` types do
different experiments correspond to? What treatments have been
applied to them? This can be obtained by using the ``-detailed`` flag:


::

    $ pysradb gse-to-srp --detailed GSE41637



=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb gse-to-srp --detailed --saveto GSE41637_metadata.tsv GSE41637

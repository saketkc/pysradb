.. _srptogse:

##########
srp-to-gse
##########

``srp-to-gse`` converts a SRA study accession ID (SRP) to GEO accession ID (GSE).

=================
Usage and options
=================

::

    $ pysradb srp-to-gse -h
    Usage: pysradb srp-to-gse [OPTIONS] SRP_ID

      Get GSE for a SRP

    Options:
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [sample_accession, run_accession]
      -h, --help     Show this message and exit.


===========================================================
Convert SRA study accession (SRP) to GEO accession ID (GSE)
===========================================================

Gene Expression Omnibus or GEO hosts processed sequencing datasets.
The raw data is available through SRA and hence we often need to
interpolate between the two.

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding GEO experiment with ID of the form ``GSEnnnn``:

::

    $ pysradb srp-to-gse SRP098789

    study_accession study_alias
    SRP098789       GSE94454

In order to obtain detailed metadata:

::

    $ pysradb srp-to-gse --detailed SRP098789


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-gse --detailed --saveto SRP098789_metadata.tsv SRP098789


.. _quickstart:

##########
Quickstart
##########

===============
Install pysradb
===============

::

    pip install pysradb

=============
Using pysradb
=============


**Download SRAmetadb.sqlite**:

::

    pysradb srametadb


**Convert SRP to SRX**:

::

    pysradb srp-to-srx SRP098789


**Convert GSE to SRP**:

::

    pysradb gse-to-srp GSE41637


==============================================
The full list of possible `pysradb` operations
==============================================

::

    $ pysradb
    Usage: pysradb [OPTIONS] COMMAND [ARGS]...

      pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.

      Citation: Pending.

    Options:
      --version   Show the version and exit.
      -h, --help  Show this message and exit.

    Commands:
      download    Download SRA project (SRPnnnn)
      gse-to-gsm  Get GSM for a GSE
      gse-to-srp  Get SRP for a GSE
      gsm-to-gse  Get GSE for a GSM
      gsm-to-srp  Get SRP for a GSM
      gsm-to-srr  Get SRR for a GSM
      gsm-to-srx  Get SRX for a GSM
      metadata    Fetch metadata for SRA project (SRPnnnn)
      metadb      Download SRAmetadb.sqlite
      search      Search SRA for matching text
      srp-to-gse  Get GSE for a SRP
      srp-to-srr  Get SRR for a SRP
      srp-to-srs  Get SRS for a SRP
      srp-to-srx  Get SRX for a SRP
      srr-to-srp  Get SRP for a SRR
      srr-to-srs  Get SRS for a SRR
      srr-to-srx  Get SRX for a SRR
      srs-to-srx  Get SRX for a SRS
      srx-to-srp  Get SRP for a SRX
      srx-to-srr  Get SRR for a SRX
      srx-to-srs  Get SRS for a SRX


.. toctree::
   :maxdepth: 1

   commands/gse-to-gsm
   commands/gse-to-srp
   commands/metadata
   commands/metadb
   commands/srp-to-gse
   commands/srp-to-srr
   commands/srp-to-srs
   commands/srp-to-srx
   commands/srr-to-srs
   commands/srr-to-srx
   commands/srs-to-srx
   commands/srx-to-srr
   commands/srx-to-srs



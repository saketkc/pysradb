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

.. toctree::
   :maxdepth: 1

   commands/gse-to-gsm
   commands/gse-to-srp
   commands/sra-metadata

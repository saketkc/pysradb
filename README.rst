#######
pysradb
#######


.. image:: https://img.shields.io/pypi/v/pysradb.svg
        :target: https://pypi.python.org/pypi/pysradb

.. image:: https://travis-ci.com/saketkc/pysradb.svg?branch=master
        :target: https://travis-ci.com/saketkc/pysradb



Python package for interacting with SRAdb and downloading datasets from SRA.

************
Installation
************

Dependecies
===========

.. code-block:: bash

   pandas>=0.23.4
   tqdm>=4.28
   aspera-client
   SRAmetadb.sqlite

SRAmetadb
=========

SRAmetadb can be downloaded as:

.. code-block:: bash

   wget -c https://starbuck1.s3.amazonaws.com/sradb/SRAmetadb.sqlite.gz && gunzip SRAmetadb.sqlite.gz

aspera-client
=============


`aspera-client` needs to be installed as well. Instructions are available here: https://downloads.asperasoft.com/connect2/
Direct download links:

- Linux: https://download.asperasoft.com/download/sw/connect/3.8.1/ibm-aspera-connect-3.8.1.161274-linux-g2.12-64.tar.gz
- MacOS: https://download.asperasoft.com/download/sw/connect/3.8.1/IBMAsperaConnectInstaller-3.8.1.161274.dmg
- Windows: https://download.asperasoft.com/download/sw/connect/3.8.1/IBMAsperaConnect-ML-3.8.1.161274.msi


Install pysradb
===============
.. code-block:: bash

   pip install -U pandas tqdm
   git clone https://github.com/saketkc/pysradb.git
   cd pysradb
   pip install -e .


********************
Interacting with SRA
********************

Fetch the metadata table (SRA-runtable)
========================================


.. code-block:: python

   from pysradb import SRAdb
   db = SRAdb('SRAmetadb.sqlite')
   df = db.sra_convert('SRP098789')
   df.head()

.. table::

    ===============  ====================  ======================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========  ============  ===============
    study_accession  experiment_accession                             experiment_title                             run_accession  taxon_id  library_selection  library_layout  library_strategy  library_source  library_name    bases      spots    adapter_spec  avg_read_length
    ===============  ====================  ======================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========  ============  ===============
    SRP098789        SRX2536403            GSM2475997: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER  SRR5227288         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2104142750  42082855                             50
    SRP098789        SRX2536404            GSM2475998: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER  SRR5227289         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2082873050  41657461                             50
    SRP098789        SRX2536405            GSM2475999: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 3; Homo sapiens; OTHER  SRR5227290         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2023148650  40462973                             50
    SRP098789        SRX2536406            GSM2476000: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER  SRR5227291         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2057165950  41143319                             50
    SRP098789        SRX2536407            GSM2476001: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER  SRR5227292         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                3027621850  60552437                             50
    ===============  ====================  ======================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========  ============  ===============

Downloading an entire project arranged experiment wise
======================================================

.. code-block:: python

   from pysradb import SRAdb
   db = SRAdb('SRAmetadb.sqlite')
   df = db.sra_convert('SRP017942')
   db.download(df)

Downloading a subset of experiments
===================================

.. code-block:: python

   df = db.sra_convert('SRP000941')
   db.download(df=df_rna, out_dir='/pysradb_downloads')()

****
Demo
****

https://nbviewer.jupyter.org/github/saketkc/pysradb/blob/master/notebooks/demo.ipynb


********
Citation
********

Pending.

A lot of functionality in `pysradb` is based on ideas from the original `SRAdb package
<https://bioconductor.org/packages/release/bioc/html/SRAdb.html>`_. Please cite the original SRAdb publication:

    Zhu, Yuelin, Robert M. Stephens, Paul S. Meltzer, and Sean R. Davis. "SRAdb: query and use public next-generation sequencing data from within R." BMC bioinformatics 14, no. 1 (2013): 19.




* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb


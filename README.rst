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

To install stable version:

.. code-block:: bash

   pip install pysradb

This step will install all the dependencies except aspera-client_.
Both Python 2 and Python 3 are supported.


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

Alternatively, you can aslo download it using `pysradb`:


.. code-block:: python

   from pysradb import download_sradb_file
   download_sradb_file()

   SRAmetadb.sqlite.gz: 2.44GB [01:10, 36.9MB/s]


.. _aspera-client:


aspera-client
=============

We strongly recommend using `aspera-client` (which uses UDP) since it enables faster downloads as compared to `ftp/http` based
downloads.

PDF intructions are available here: https://downloads.asperasoft.com/connect2/.

Direct download links:

- Linux: https://download.asperasoft.com/download/sw/connect/3.8.1/ibm-aspera-connect-3.8.1.161274-linux-g2.12-64.tar.gz
- MacOS: https://download.asperasoft.com/download/sw/connect/3.8.1/IBMAsperaConnectInstaller-3.8.1.161274.dmg
- Windows: https://download.asperasoft.com/download/sw/connect/3.8.1/IBMAsperaConnect-ML-3.8.1.161274.msi

Once you download the tar relevant to your OS, say linux, follow these steps to install aspera:

.. code-block:: bash

   tar -zxvf ibm-aspera-connect-3.8.1.161274-linux-g2.12-64.tar.gz
   bash ibm-aspera-connect-3.8.1.161274-linux-g2.12-64.sh
   Installing IBM Aspera Connect
   Deploying IBM Aspera Connect (/home/saket/.aspera/connect) for the current user only.
   Install complete.


Installing pysradb in development mode
======================================

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
   df = db.sra_metadata('SRP098789')
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
   df = db.sra_metadata('SRP017942')
   db.download(df)

Downloading a subset of experiments
===================================

.. code-block:: python

   df = db.sra_metadata('SRP000941')
   print(df.library_strategy.unique())
   ['ChIP-Seq' 'Bisulfite-Seq' 'RNA-Seq' 'WGS' 'OTHER']


.. code-block:: python

   df_rna = df[df.library_strategy == 'RNA-Seq']
   db.download(df=df_rna, out_dir='/pysradb_downloads')()



Searching for datasets
======================

Search for all datasets where `ribosome profiling` appears somewhere
in the description:

.. code-block:: python


   df = db.search_sra(search_str='"ribosome profiling"')
   df.head()

.. table::

    ===============  ====================  =======================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========
    study_accession  experiment_accession                     experiment_title                      run_accession  taxon_id  library_selection  library_layout  library_strategy  library_source  library_name    bases      spots
    ===============  ====================  =======================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========
    DRP003075        DRX019536             Illumina Genome Analyzer IIx sequencing of SAMD00018584  DRR021383         83333  other              SINGLE -        OTHER             TRANSCRIPTOMIC  GAII05_3       978776480  12234706
    DRP003075        DRX019537             Illumina Genome Analyzer IIx sequencing of SAMD00018585  DRR021384         83333  other              SINGLE -        OTHER             TRANSCRIPTOMIC  GAII05_4       894201680  11177521
    DRP003075        DRX019538             Illumina Genome Analyzer IIx sequencing of SAMD00018586  DRR021385         83333  other              SINGLE -        OTHER             TRANSCRIPTOMIC  GAII05_5       931536720  11644209
    DRP003075        DRX019540             Illumina Genome Analyzer IIx sequencing of SAMD00018588  DRR021387         83333  other              SINGLE -        OTHER             TRANSCRIPTOMIC  GAII07_4      2759398700  27593987
    DRP003075        DRX019541             Illumina Genome Analyzer IIx sequencing of SAMD00018589  DRR021388         83333  other              SINGLE -        OTHER             TRANSCRIPTOMIC  GAII07_5      2386196500  23861965
    ===============  ====================  =======================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========

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


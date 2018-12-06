#######
pysradb
#######


.. image:: https://img.shields.io/pypi/v/pysradb.svg
        :target: https://pypi.python.org/pypi/pysradb

.. image:: https://travis-ci.com/saketkc/pysradb.svg?branch=master
        :target: https://travis-ci.com/saketkc/pysradb

.. image:: https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square
        :target: http://bioconda.github.io/recipes/pysradb/README.html



Python package for interacting with SRAdb and downloading datasets from SRA.

************
Installation
************


To install stable version using `pip`:

.. code-block:: bash

   pip install pysradb

Alternatively, if you use conda:

.. code-block:: bash

   conda install -c bioconda pysradb

This step will install all the dependencies except aspera-client_ (which is not required, but highly recommended).
Both Python 2 and Python 3 are supported.


Dependecies
===========

.. code-block:: bash

   pandas>=0.23.4
   tqdm>=4.28
   aspera-client
   SRAmetadb.sqlite

Downloading SRAmetadb
=====================

We need a SQLite database file that has preprocessed metadata made available by the
`SRAdb <https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-14-19>`_ project.

SRAmetadb can be downloaded using:

.. code-block:: bash

   wget -c https://starbuck1.s3.amazonaws.com/sradb/SRAmetadb.sqlite.gz && gunzip SRAmetadb.sqlite.gz

Alternatively, you can also download it using `pysradb`:


.. code-block:: python

   from pysradb import download_sradb_file
   download_sradb_file()

   SRAmetadb.sqlite.gz: 2.44GB [01:10, 36.9MB/s]


.. _aspera-client:


aspera-client
=============

We strongly recommend using `aspera-client` (which uses UDP) since it `warrants faster downloads <http://www.skullbox.net/tcpudp.php>`_ as compared to `ftp/http` based downloads.

PDF intructions are available on IBM's `website <https://downloads.asperasoft.com/connect2/>`_.

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

Use Case 1: Fetch the metadata table (SRA-runtable)
===================================================

The simplest use case of `pysradb` is when you apriopri know the SRA project ID (SRP)
and would simply want to fetch the metadata associated with it. This is generally
reflected in the `SraRunTable.txt` that you get from NCBI's website.
See an `example <https://www.ncbi.nlm.nih.gov/Traces/study/?acc=SRP098789>`_ of a SraRunTable.


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

The metadata is returned as a `pandas` dataframe and hence allows you to perform
all regular select/query operations available through `pandas`.

Use Case 2: Downloading an entire project arranged experiment wise
==================================================================

Once you have fetched the metadata and made sure, this is the project
you were looking for, you would want to download everything at once.
NCBI follows this hiererachy: `SRP => SRX => SRR`. Each `SRP` (project) has multiple
`SRX` (experiments) and each `SRX` in turn has multiple `SRR` (runs) inside it.
We want to mimick this hiereachy in our downloads. The reason to do that is simple:
in most cases you care about `SRX` the most, and would want to "merge" your SRRs
in one way or the other. Having this hierearchy ensures your downstream code
can handle such cases easily, without worrying about which runs (SRR) need to be merged.

We strongly recommend installing `aspera-client` which uses UDP and is `designed to be faster <http://www.skullbox.net/tcpudp.php>`_.

.. code-block:: python

   from pysradb import SRAdb
   db = SRAdb('SRAmetadb.sqlite')
   df = db.sra_metadata('SRP017942')
   db.download(df)

Use Case 3: Downloading a subset of experiments
===============================================

Often, you need to process only a smaller set of samples from a project (SRP).
Consider this project which has data spanning four assays.

.. code-block:: python

   df = db.sra_metadata('SRP000941')
   print(df.library_strategy.unique())
   ['ChIP-Seq' 'Bisulfite-Seq' 'RNA-Seq' 'WGS' 'OTHER']


But, you might be only interested in analyzing the `RNA-seq` samples and would just want to download that subset.
This is simple using `pysradb` since the metadata can be subset just as you would subset a dataframe in
pandas.


.. code-block:: python

   df_rna = df[df.library_strategy == 'RNA-Seq']
   db.download(df=df_rna, out_dir='/pysradb_downloads')()


Use Case 4: Getting cell-type/treatment information from sample_attributes
==========================================================================

Cell type/tissue informations is usually hidden in the `sample_attributes` column,
which can be expanded:

.. code-block:: python

   from pysradb.filter_attrs import expand_sample_attribute_columns
   df = db.sra_metadata('SRP017942')
   expand_sample_attribute_columns(df).head()


.. table::

    ===============  ====================  =====================================================================  =========================  ========================================================================================================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  =========  ============  ===============  ==========  ==========  ===========  ================  ===============================
    study_accession  experiment_accession                            experiment_title                               experiment_attribute                                                                         sample_attribute                                                                      run_accession  taxon_id  library_selection  library_layout  library_strategy  library_source  library_name    bases       spots    adapter_spec  avg_read_length  assay_type  cell_line   source_name  transfected_with             treatment
    ===============  ====================  =====================================================================  =========================  ========================================================================================================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  =========  ============  ===============  ==========  ==========  ===========  ================  ===============================
    SRP017942        SRX217028             GSM1063575: 293T_GFP; Homo sapiens; RNA-Seq                            GEO Accession: GSM1063575  source_name: 293T cells || cell line: 293T cells || transfected with: 3XFLAG-GFP || assay type: Riboseq                                                   SRR648667          9606  other              SINGLE -        RNA-Seq           TRANSCRIPTOMIC                1806641316   50184481                             36  riboseq     293t cells  293t cells   3xflag-gfp        NaN
    SRP017942        SRX217029             GSM1063576: 293T_GFP_2hrs_severe_Heat_Shock; Homo sapiens; RNA-Seq     GEO Accession: GSM1063576  source_name: 293T cells || cell line: 293T cells || transfected with: 3XFLAG-GFP || treatment: severe heat shock (44C 2 hours) || assay type: Riboseq     SRR648668          9606  other              SINGLE -        RNA-Seq           TRANSCRIPTOMIC                3436984836   95471801                             36  riboseq     293t cells  293t cells   3xflag-gfp        severe heat shock (44c 2 hours)
    SRP017942        SRX217030             GSM1063577: 293T_Hspa1a; Homo sapiens; RNA-Seq                         GEO Accession: GSM1063577  source_name: 293T cells || cell line: 293T cells || transfected with: 3XFLAG-Hspa1a || assay type: Riboseq                                                SRR648669          9606  other              SINGLE -        RNA-Seq           TRANSCRIPTOMIC                3330909216   92525256                             36  riboseq     293t cells  293t cells   3xflag-hspa1a     NaN
    SRP017942        SRX217031             GSM1063578: 293T_Hspa1a_2hrs_severe_Heat_Shock; Homo sapiens; RNA-Seq  GEO Accession: GSM1063578  source_name: 293T cells || cell line: 293T cells || transfected with: 3XFLAG-Hspa1a || treatment: severe heat shock (44C 2 hours) || assay type: Riboseq  SRR648670          9606  other              SINGLE -        RNA-Seq           TRANSCRIPTOMIC                3622123512  100614542                             36  riboseq     293t cells  293t cells   3xflag-hspa1a     severe heat shock (44c 2 hours)
    SRP017942        SRX217956             GSM794854: 3T3-Control-Riboseq; Mus musculus; RNA-Seq                  GEO Accession: GSM794854   source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq                                                               SRR649752         10090  cDNA               SINGLE -        RNA-Seq           TRANSCRIPTOMIC                 594945396   16526261                             36  riboseq     3t3 cells   3t3 cells    NaN               control
    ===============  ====================  =====================================================================  =========================  ========================================================================================================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  =========  ============  ===============  ==========  ==========  ===========  ================  ===============================


Use Case 5: Searching for datasets
==================================

Another common operation that we do on SRA is seach, plain text search.


If you want to look up for all projects where `ribosome profiling` appears somewhere
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

Again, the results are available as a `pandas` dataframe and hence
you can perform all subset operations post your query. Your query doesn't need
to be exact.

****
Demo
****

https://nbviewer.jupyter.org/github/saketkc/pysradb/blob/master/notebooks/demo.ipynb


********
Citation
********

Pending.

A lot of functionality in `pysradb` is based on ideas from the original `SRAdb package <https://bioconductor.org/packages/release/bioc/html/SRAdb.html>`_. Please cite the original SRAdb publication:

    Zhu, Yuelin, Robert M. Stephens, Paul S. Meltzer, and Sean R. Davis. "SRAdb: query and use public next-generation sequencing data from within R." BMC bioinformatics 14, no. 1 (2013): 19.




* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb


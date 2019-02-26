#######
pysradb
#######

.. image:: https://zenodo.org/badge/159590788.svg
    :target: https://zenodo.org/badge/latestdoi/159590788

.. image:: https://img.shields.io/pypi/v/pysradb.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pysradb

.. image:: https://img.shields.io/travis/saketkc/pysradb.svg?style=flat-square
    :target: https://travis-ci.com/saketkc/pysradb

.. image:: https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square
    :target: http://bioconda.github.io/recipes/pysradb/README.html

.. image:: https://codecov.io/gh/saketkc/pysradb/branch/master/graph/badge.svg?style=flat-square
    :target: https://codecov.io/gh/saketkc/pysradb

Python package for interacting with SRAdb and downloading datasets from SRA.
(python3 only!)

.. raw:: html

    <a href="https://asciinema.org/a/0C3SjYmPTkkemldprUpdVhiKx?speed=5&autoplay=1" target="_blank"><img src="https://asciinema.org/a/0C3SjYmPTkkemldprUpdVhiKx.svg" /></a>


*********
CLI Usage
*********

``pysradb`` supports command line ussage. The documentation
is in progress. See  `cmdline <https://github.com/saketkc/pysradb/blob/master/docs/cmdline.rst>`_ for
some quick usage instructions. See `quickstart <https://www.saket-choudhary.me/pysradb/quickstart.html#the-full-list-of-possible-pysradb-operations>`_ for
a list of instructions for each sub-command.


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
      srr-to-gsm  Get GSM for a SRR
      srp-to-srx  Get SRX for a SRP
      srr-to-srp  Get SRP for a SRR
      srr-to-srs  Get SRS for a SRR
      srr-to-srx  Get SRX for a SRR
      srs-to-srx  Get SRX for a SRS
      srx-to-srp  Get SRP for a SRX
      srx-to-srr  Get SRR for a SRX
      srx-to-srs  Get SRS for a SRX


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
If you have an existing environment with a lot of pre-installed packages, conda might be `slow <https://github.com/bioconda/bioconda-recipes/issues/13774>`_.
Please consider creating a new enviroment for ``pysradb``:

.. code-block:: bash

   conda create -c bioconda -n pysradb PYTHON=3 pysradb

Dependecies
===========

.. code-block:: bash

   pandas>=0.23.4
   tqdm>=4.28
   click>=7.0
   aspera-client
   SRAmetadb.sqlite

Downloading SRAmetadb
=====================

We need a SQLite database file that has preprocessed metadata made available by the
`SRAdb <https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-14-19>`_ project.

SRAmetadb can be downloaded using:

.. code-block:: bash

   wget -c https://starbuck1.s3.amazonaws.com/sradb/SRAmetadb.sqlite.gz && gunzip SRAmetadb.sqlite.gz

Alternatively, you can also download it using ``pysradb``, which by default downloads it into your
current working directory:


::

    $ pysradb metadb

You can also specify an alternate directory for download by supplying the ``--out-dir <OUT_DIR>`` argument.

.. _aspera-client:


aspera-client
=============

We strongly recommend using ``aspera-client`` (which uses UDP) since it `warrants faster downloads <http://www.skullbox.net/tcpudp.php>`_ as compared to ``ftp/http`` based downloads.

PDF intructions are available on IBM's `website <https://downloads.asperasoft.com/connect2/>`_.

Direct download links:

- `Linux <https://download.asperasoft.com/download/sw/connect/3.8.1/ibm-aspera-connect-3.8.1.161274-linux-g2.12-64.tar.gz>`_
- `MacOS <https://download.asperasoft.com/download/sw/connect/3.8.1/IBMAsperaConnectInstaller-3.8.1.161274.dmg>`_
- `Windows: <https://download.asperasoft.com/download/sw/connect/3.8.1/IBMAsperaConnect-ML-3.8.1.161274.msi>`_

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



*************
Using pysradb
*************

Please see `usage_scenarios <https://saket-choudhary.me/pysradb/usage_scenarios.html>`_ for a few usage scenarios.
Here are few hand-picked examples.


Getting SRA metadata
====================

::

    $ pysradb metadata --db ./SRAmetadb.sqlite SRP000941 --assay --desc --expand | head

    study_accession experiment_accession sample_accession run_accession library_strategy batch         biomaterial_provider             biomaterial_type cell_type    collection_method differentiation_method                                                                                                                     differentiation_stage                                                                disease                                                          donor_age donor_ethnicity                 donor_health_status                                                                                 donor_id donor_sex line          lineage                                                               medium                                                                                                                                                                                                   molecule     passage                             sample_term_id  sex     source_name              tissue                   tissue_depot tissue_type
    SRP000941       SRX006235            SRS004118        SRR018454     ChIP-Seq         NaN           cellular dynamics international  cell line        NaN          NaN               none                                                                                                                                       none                                                                                 none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            embryonic stem cell                                                   mteser                                                                                                                                                                                                   genomic dna  between 30 and 50                   efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006236            SRS004118        SRR018456     ChIP-Seq         NaN           cellular dynamics international  cell line        NaN          NaN               none                                                                                                                                       none                                                                                 none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            embryonic stem cell                                                   mteser                                                                                                                                                                                                   genomic dna  between 30 and 50                   efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006237            SRS004118        SRR018455     ChIP-Seq         NaN           cellular dynamics international  cell line        NaN          NaN               none                                                                                                                                       none                                                                                 none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            embryonic stem cell                                                   mteser                                                                                                                                                                                                   genomic dna  between 30 and 50                   efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019072     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019080     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019081     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019082     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019083     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019084     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN


Getting detailed SRA metadata
=============================

::

    $ pysradb metadata --db ./SRAmetadb.sqlite SRP075720 --detailed --expand | head

    study_accession experiment_accession sample_accession run_accession experiment_title                                  experiment_attribute        taxon_id library_selection library_layout library_strategy library_source  library_name  bases      spots   adapter_spec  avg_read_length developmental_stage retina_id source_name                tissue
    SRP075720       SRX1800089           SRS1467259       SRR3587529    GSM2177186: Kcng4_1Ra_A10; Mus musculus; RNA-Seq  GEO Accession: GSM2177186  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         79101650   1582033  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800090           SRS1467260       SRR3587530    GSM2177187: Kcng4_1Ra_A11; Mus musculus; RNA-Seq  GEO Accession: GSM2177187  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         84573650   1691473  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800091           SRS1467261       SRR3587531    GSM2177188: Kcng4_1Ra_A12; Mus musculus; RNA-Seq  GEO Accession: GSM2177188  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         77835550   1556711  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800092           SRS1467262       SRR3587532    GSM2177189: Kcng4_1Ra_A1; Mus musculus; RNA-Seq   GEO Accession: GSM2177189  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         73905150   1478103  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800093           SRS1467263       SRR3587533    GSM2177190: Kcng4_1Ra_A2; Mus musculus; RNA-Seq   GEO Accession: GSM2177190  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         77193150   1543863  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800094           SRS1467264       SRR3587534    GSM2177191: Kcng4_1Ra_A3; Mus musculus; RNA-Seq   GEO Accession: GSM2177191  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         59205550   1184111  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800095           SRS1467265       SRR3587535    GSM2177192: Kcng4_1Ra_A4; Mus musculus; RNA-Seq   GEO Accession: GSM2177192  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         61794700   1235894  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800096           SRS1467266       SRR3587536    GSM2177193: Kcng4_1Ra_A5; Mus musculus; RNA-Seq   GEO Accession: GSM2177193  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         78437650   1568753  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800097           SRS1467267       SRR3587537    GSM2177194: Kcng4_1Ra_A6; Mus musculus; RNA-Seq   GEO Accession: GSM2177194  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         77392700   1547854  None         50.0             p17                 1ra       mus musculus retina__ p17  retina


Converting SRP to GSE
=====================

::

    $ pysradb srp-to-gse --db ./SRAmetadb.sqlite SRP075720

    study_accession study_alias
    SRP075720       GSE81903


Converting GSM to SRP
=====================

::

    $ pysradb gsm-to-srp --db ./SRAmetadb.sqlite GSM2177186

    experiment_alias study_accession
    GSM2177186       SRP075720


Converting GSM to GSE
=====================

::

    $ pysradb gsm-to-gse --db ./SRAmetadb.sqlite GSM2177186

    experiment_alias study_alias
    GSM2177186       GSE81903


Converting GSM to SRX
=====================

::

    $ pysradb gsm-to-srx --db ./SRAmetadb.sqlite GSM2177186

    experiment_alias experiment_accession
    GSM2177186       SRX1800089


Converting GSM to SRR
=====================

::

    $ pysradb gsm-to-srr --db ./SRAmetadb.sqlite GSM2177186

    experiment_alias run_accession
    GSM2177186       SRR3587529


Complete Metadata for any record
================================

Use the ``--detailed`` flag:

::

    $ pysradb gsm-to-srr --db ./SRAmetadb.sqlite GSM2177186 --detailed --desc --expand

    experiment_alias run_accession experiment_accession sample_accession study_accession run_alias      sample_alias study_alias developmental_stage retina_id source_name                tissue
    GSM2177186       SRR3587529    SRX1800089           SRS1467259       SRP075720       GSM2177186_r1  GSM2177186   GSE81903    p17                 1ra       mus musculus retina__ p17  retina


Getting only the assay type
===========================

::

    $ pysradb metadata SRP000941 --db ./SRAmetadb.sqlite --assay  | tr -s '  ' | cut -f5 -d ' ' | sort | uniq -c

    999 Bisulfite-Seq
    768 ChIP-Seq
      1 library_strategy
    121 OTHER
    353 RNA-Seq
     28 WGS


Downloading entire project
==========================

``pysradb`` makes it super easy to download datasets from SRA.

::

    $ pysradb download --db ./SRAmetadb.sqlite --out-dir ./pysradb_downloads -p SRP063852

Downloads are organized by ``SRP/SRX/SRR`` mimicking the hiererachy of SRA projects.


Downloading only certain samples of interest
============================================

::

    $ pysradb metadata SRP000941 --assay | grep 'study\|RNA-Seq' | pysradb download

This will download all ``RNA-seq`` samples coming from this project using ``aspera-client``, if available.
Alternatively, it can also use ``wget``.

**************
Demo Notebooks
**************

These notebooks document all the possible features of `pysradb`:

1. `Python API usage <https://nbviewer.jupyter.org/github/saketkc/pysradb/blob/master/notebooks/01.SRAdb-demo.ipynb>`_
2. `Command line usage <https://nbviewer.jupyter.org/github/saketkc/pysradb/blob/master/notebooks/03.CommandLine-demo.ipynb>`_



********
Citation
********

Zenodo archive: https://zenodo.org/badge/latestdoi/159590788

DOI: 10.5281/zenodo.2306881

A lot of functionality in ``pysradb`` is based on ideas from the original `SRAdb package <https://bioconductor.org/packages/release/bioc/html/SRAdb.html>`_. Please cite the original SRAdb publication:

    Zhu, Yuelin, Robert M. Stephens, Paul S. Meltzer, and Sean R. Davis. "SRAdb: query and use public next-generation sequencing data from within R." BMC bioinformatics 14, no. 1 (2013): 19.


* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb

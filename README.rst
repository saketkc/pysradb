.. image:: https://raw.githubusercontent.com/saketkc/pysradb/master/docs/_static/pysradb_v3.png
    :target: https://raw.githubusercontent.com/saketkc/pysradb/master/docs/_static/pysradb_v3.png

#####################################################################################
pysradb: Python package for interacting with SRAdb and downloading datasets from SRA.
#####################################################################################






.. image:: https://img.shields.io/pypi/v/pysradb.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pysradb

.. image:: https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square
    :target: http://bioconda.github.io/recipes/pysradb/README.html

.. image:: https://zenodo.org/badge/159590788.svg
    :target: https://zenodo.org/badge/latestdoi/159590788

.. image:: https://img.shields.io/travis/saketkc/pysradb.svg?style=flat-square
    :target: https://travis-ci.com/saketkc/pysradb


.. image:: https://asciinema.org/a/0C3SjYmPTkkemldprUpdVhiKx.svg
    :target: https://asciinema.org/a/0C3SjYmPTkkemldprUpdVhiKx?speed=5&autoplay=1
    
***********
Publication
***********

 `pysradb: A Python package to query next-generation sequencing metadata and data from NCBI Sequence Read Archive <https://f1000research.com/articles/8-532/v1>`_ 
 
 
 Presentation slides from BOSC (ISMB-ECCB) 2019: https://f1000research.com/slides/8-1183

*********
CLI Usage
*********

``pysradb`` supports command line ussage. The documentation
is in progress. See  `cmdline <https://github.com/saketkc/pysradb/blob/master/docs/cmdline.rst>`_ for
some quick usage instructions. See `quickstart <https://www.saket-choudhary.me/pysradb/quickstart.html#the-full-list-of-possible-pysradb-operations>`_ for
a list of instructions for each sub-command.


::

   $ pysradb
    usage: pysradb [-h] [--version] [--citation]
                   {metadb,metadata,download,search,gse-to-gsm,gse-to-srp,gsm-to-gse,gsm-to-srp,gsm-to-srr,gsm-to-srs,gsm-to-srx,srp-to-gse,srp-to-srr,srp-to-srs,srp-to-srx,srr-to-gsm,srr-to-srp,srr-to-srs,srr-to-srx,srs-to-gsm,srs-to-srx,srx-to-srp,srx-to-srr,srx-to-srs}
                   ...

    pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.
    version: 0.9.0.
    Citation: 10.12688/f1000research.18676.1

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --citation            how to cite

    subcommands:
      {metadb,metadata,download,search,gse-to-gsm,gse-to-srp,gsm-to-gse,gsm-to-srp,gsm-to-srr,gsm-to-srs,gsm-to-srx,srp-to-gse,srp-to-srr,srp-to-srs,srp-to-srx,srr-to-gsm,srr-to-srp,srr-to-srs,srr-to-srx,srs-to-gsm,srs-to-srx,srx-to-srp,srx-to-srr,srx-to-srs}
        metadb              Download SRAmetadb.sqlite
        metadata            Fetch metadata for SRA project (SRPnnnn)
        download            Download SRA project (SRPnnnn)
        search              Search SRA for matching text
        gse-to-gsm          Get GSM for a GSE
        gse-to-srp          Get SRP for a GSE
        gsm-to-gse          Get GSE for a GSM
        gsm-to-srp          Get SRP for a GSM
        gsm-to-srr          Get SRR for a GSM
        gsm-to-srs          Get SRS for a GSM
        gsm-to-srx          Get SRX for a GSM
        srp-to-gse          Get GSE for a SRP
        srp-to-srr          Get SRR for a SRP
        srp-to-srs          Get SRS for a SRP
        srp-to-srx          Get SRX for a SRP
        srr-to-gsm          Get GSM for a SRR
        srr-to-srp          Get SRP for a SRR
        srr-to-srs          Get SRS for a SRR
        srr-to-srx          Get SRX for a SRR
        srs-to-gsm          Get GSM for a SRS
        srs-to-srx          Get SRX for a SRS
        srx-to-srp          Get SRP for a SRX
        srx-to-srr          Get SRR for a SRX
        srx-to-srs          Get SRS for a SRX


**********
Quickstart
**********

A Google Colaboratory version of most used commands are available in this `Colab Notebook <https://colab.research.google.com/drive/1C60V-jkcNZiaCra_V5iEyFs318jgVoUR>`_ . Note that this does not require you to download the heavy SQLite file and uses the `SRAWeb` mode (explained below).

************
Installation
************


To install stable version using `pip`:

.. code-block:: bash

   pip install pysradb

Alternatively, if you use conda:

.. code-block:: bash

   conda install -c bioconda pysradb

This step will install all the dependencies.
If you have an existing environment with a lot of pre-installed packages, conda might be `slow <https://github.com/bioconda/bioconda-recipes/issues/13774>`_.
Please consider creating a new enviroment for ``pysradb``:

.. code-block:: bash

   conda create -c bioconda -n pysradb PYTHON=3 pysradb

Dependecies
===========

.. code-block:: bash

   pandas==0.25.3
   tqdm==4.41.1
   requests==2.22.0
   xmltodict=0.12.0
   sra-tools (required only if you want to also download)

Installing sratools
===================

NCBI has slowly transitioned towards using Google cloud for storing SRA files. As such
the ftp links are slowly getting obsolete. With release ``0.9.5``, ``pysradb`` has
moved to utilizing ``srapath``  available through NCBI's ``sra-tools`` for getting
the SRA location. Thus ``aspera-client`` is no longer required. But, ``sra-tools``
is now a requirement and can be installed through bioconda. We are in the process of
doing away with this requirement completely soon.

Downloading SRAmetadb (optional)
=================================

``pysradb`` can utilize a SQLite database file that has preprocessed metadata made available by the
`SRAdb <https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-14-19>`_ project.
Though, with the release ``0.9.5``, this database file is not a hard requirement for any of the operations.



SRAmetadb can be downloaded using:

.. code-block:: bash

   wget -c https://starbuck1.s3.amazonaws.com/sradb/SRAmetadb.sqlite.gz && gunzip SRAmetadb.sqlite.gz

Alternatively, you can also download it using ``pysradb``, which by default downloads it into your
current working directory:


::

    $ pysradb metadb

You can also specify an alternate directory for download by supplying the ``--out-dir <OUT_DIR>`` argument.


Installing pysradb in development mode
======================================

.. code-block:: bash

   pip install -U pandas tqdm requests xmltodict
   git clone https://github.com/saketkc/pysradb.git
   cd pysradb
   pip install -e .



*************
Using pysradb
*************

Please see `usage_scenarios <https://saket-choudhary.me/pysradb/usage_scenarios.html>`_ for a few usage scenarios.
Here are few hand-picked examples.


Mode: SRAmetadb or SRAWeb
=========================

``pysradb``'s initial versions were completely dependent on the ``SRAmnetadb.sqlite`` file made available by the ``SRAdb`` project, we refer to this as the ``SRAmetadb`` mode. However, with ```pysradb 0.9.5``, the depedence on the SQLite file has been made optional. In the abseence of the SQLite file, the operations are performed usiNCBi's ``esrarch`` and ``esummary`` interface, a mode which we refer to as the ``SRAweb`` mode.  All the operations
with the exception of ``search`` can be performed withoudownloading the SQLite file.
NOTE: The additional flags such as ``--desc``, ``-detailed`` and ``-expand`` are currently not fully supported in the ``SRAweb`` mode and will be supported in a future release. However, all the basic funcuionality of interconverting one ID to another is available in both ``SRAweb`` and ``SRAmetadb`` mode.



Search
======

Search for all projects containing "ribosome profiling":

::

   $  pysradb search "ribosome profiling" | head

    study_accession experiment_accession sample_accession run_accession
    DRP000927       DRX002899            DRS002983        DRR003575
    DRP000927       DRX002900            DRS002992        DRR003576
    DRP000927       DRX002901            DRS003001        DRR003577
    DRP000927       DRX002902            DRS003010        DRR003578
    DRP000927       DRX002903            DRS003019        DRR003579
    DRP000927       DRX002904            DRS003028        DRR003580
    DRP000927       DRX002905            DRS003037        DRR003581
    DRP000927       DRX002906            DRS003038        DRR003582
    DRP003075       DRX019536            DRS026974        DRR021383



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

    $ pysradb srp-to-gse SRP075720

    study_accession study_alias
    SRP075720       GSE81903


Converting GSM to SRP
=====================

::

    $ pysradb gsm-to-srp GSM2177186

    experiment_alias study_accession
    GSM2177186       SRP075720


Converting GSM to GSE
=====================

::

    $ pysradb gsm-to-gse GSM2177186

    experiment_alias study_alias
    GSM2177186       GSE81903


Converting GSM to SRX
=====================

::

    $ pysradb gsm-to-srx GSM2177186

    experiment_alias experiment_accession
    GSM2177186       SRX1800089


Converting GSM to SRR
=====================

::

    $ pysradb gsm-to-srr GSM2177186

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

    $ pysradb download --out-dir ./pysradb_downloads -p SRP063852

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

Choudhary, Saket. "pysradb: A Python Package to Query next-Generation Sequencing Metadata and Data from NCBI Sequence Read Archive." F1000Research, vol. 8, F1000 (Faculty of 1000 Ltd), Apr. 2019, p. 532 (https://f1000research.com/articles/8-532/v1)

::

    @article{Choudhary2019,
    doi = {10.12688/f1000research.18676.1},
    url = {https://doi.org/10.12688/f1000research.18676.1},
    year = {2019},
    month = apr,
    publisher = {F1000 (Faculty of 1000 Ltd)},
    volume = {8},
    pages = {532},
    author = {Saket Choudhary},
    title = {pysradb: A {P}ython package to query next-generation sequencing metadata and data from {NCBI} {S}equence {R}ead {A}rchive},
    journal = {F1000Research}
    }


Zenodo archive: https://zenodo.org/badge/latestdoi/159590788

Zenodo DOI: 10.5281/zenodo.2306881

A lot of functionality in ``pysradb`` is based on ideas from the original `SRAdb package <https://bioconductor.org/packages/release/bioc/html/SRAdb.html>`_. Please cite the original SRAdb publication:

    Zhu, Yuelin, Robert M. Stephens, Paul S. Meltzer, and Sean R. Davis. "SRAdb: query and use public next-generation sequencing data from within R." BMC bioinformatics 14, no. 1 (2013): 19.


* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb

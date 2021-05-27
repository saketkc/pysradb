######################################################################################
A Python package for retrieving metadata and downloading datasets from SRA/ENA/GEO
######################################################################################

.. image:: https://img.shields.io/pypi/v/pysradb.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pysradb

.. image:: https://anaconda.org/bioconda/pysradb/badges/version.svg
    :target: https://anaconda.org/bioconda/pysradb/badges/version.svg
    
.. image:: https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square
    :target: http://bioconda.github.io/recipes/pysradb/README.html

.. image:: https://zenodo.org/badge/159590788.svg
    :target: https://zenodo.org/badge/latestdoi/159590788

.. image:: https://github.com/saketkc/pysradb/workflows/push/badge.svg
    :target: https://github.com/saketkc/pysradb/actions
   
.. image:: https://anaconda.org/bioconda/pysradb/badges/downloads.svg
    :target: http://bioconda.github.io/recipes/pysradb/README.html



*************
Documentation
*************

https://saketkc.github.io/pysradb


*********
CLI Usage
*********

``pysradb`` supports command line ussage. See `CLI <https://saket-choudhary.me/pysradb/cmdline.html>`_ instructions or  `quickstart guide <https://www.saket-choudhary.me/pysradb/quickstart.html>`_.
 


::

   $ pysradb
    usage: pysradb [-h] [--version] [--citation]
                   {metadata,download,search,gse-to-gsm,gse-to-srp,gsm-to-gse,gsm-to-srp,gsm-to-srr,gsm-to-srs,gsm-to-srx,srp-to-gse,srp-to-srr,srp-to-srs,srp-to-srx,srr-to-gsm,srr-to-srp,srr-to-srs,srr-to-srx,srs-to-gsm,srs-to-srx,srx-to-srp,srx-to-srr,srx-to-srs}
                   ...

    pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.
    version: 1.0.1
    Citation: 10.12688/f1000research.18676.1

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --citation            how to cite

    subcommands:
      {metadata,download,search,gse-to-gsm,gse-to-srp,gsm-to-gse,gsm-to-srp,gsm-to-srr,gsm-to-srs,gsm-to-srx,srp-to-gse,srp-to-srr,srp-to-srs,srp-to-srx,srr-to-gsm,srr-to-srp,srr-to-srs,srr-to-srx,srs-to-gsm,srs-to-srx,srx-to-srp,srx-to-srr,srx-to-srs}
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

A Google Colaboratory version of most used commands are available in this `Colab Notebook <https://colab.research.google.com/drive/1C60V-jkcNZiaCra_V5iEyFs318jgVoUR>`_ . Note that this requires only an active internet connection (no additional downloads are made).

The following notebooks document all the possible features of `pysradb`:

1. `Python API <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/01.Python-API_demo.ipynb>`_
2. `Downloading datasets from SRA - command line <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/02.Commandline_download.ipynb>`_
3. `Parallely download multiple datasets - Python API <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/03.ParallelDownload.ipynb>`_
4. `Converting SRA-to-fastq - command line (requires conda) <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/04.SRA_to_fastq_conda.ipynb>`_
5. `Downloading subsets of a project - Python API <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/05.Downloading_subsets_of_a_project.ipynb>`_
6. `Download BAMs <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/06.Download_BAMs.ipynb>`_
7. `Metadata for multiple SRPs <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/07.Multiple_SRPs.ipynb>`_
8. `Multithreaded fastq downloads using Aspera Client <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/08.pysradb_ascp_multithreaded.ipynb>`_
9. `Searching SRA/GEO/ENA <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/09.Query_Search.ipynb>`_



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

   conda create -c bioconda -n pysradb PYTHON=3.7 pysradb

Dependecies
===========

.. code-block:: bash

   pandas
   requests
   tqdm
   xmltodict


Installing pysradb in development mode
======================================

.. code-block:: bash

   git clone https://github.com/saketkc/pysradb.git
   cd pysradb && pip install -r requirements.txt
   pip install -e .



*************
Using pysradb
*************



Obtaining SRA metadata
======================

::

    $ pysradb metadata SRP000941 | head

    study_accession experiment_accession experiment_title                                                                                                                 experiment_desc                                                                                                                  organism_taxid  organism_name library_strategy library_source  library_selection sample_accession sample_title instrument                    total_spots total_size    run_accession run_total_spots run_total_bases
    SRP000941       SRX056722                                                                         Reference Epigenome: ChIP-Seq Analysis of H3K27ac in hESC H1 Cells                                                               Reference Epigenome: ChIP-Seq Analysis of H3K27ac in hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC    ChIP            SRS184466                              Illumina HiSeq 2000    26900401     531654480   SRR179707     26900401         807012030
    SRP000941       SRX027889                                                                            Reference Epigenome: ChIP-Seq Analysis of H2AK5ac in hESC Cells                                                                  Reference Epigenome: ChIP-Seq Analysis of H2AK5ac in hESC Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC    ChIP            SRS116481                      Illumina Genome Analyzer II    37528590     779578968   SRR067978     37528590        1351029240
    SRP000941       SRX027888                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS116483                      Illumina Genome Analyzer II    13603127    3232309537   SRR067977     13603127         489712572
    SRP000941       SRX027887                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS116562                      Illumina Genome Analyzer II    22430523     506327844   SRR067976     22430523         807498828
    SRP000941       SRX027886                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS116560                      Illumina Genome Analyzer II    15342951     301720436   SRR067975     15342951         552346236
    SRP000941       SRX027885                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS116482                      Illumina Genome Analyzer II    39725232     851429082   SRR067974     39725232        1430108352
    SRP000941       SRX027884                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS116481                      Illumina Genome Analyzer II    32633277     544478483   SRR067973     32633277        1174797972
    SRP000941       SRX027883                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS004118                      Illumina Genome Analyzer II    22150965    3262293717   SRR067972      9357767         336879612
    SRP000941       SRX027883                                                                                     Reference Epigenome: ChIP-Seq Input from hESC H1 Cells                                                                           Reference Epigenome: ChIP-Seq Input from hESC H1 Cells  9606            Homo sapiens       ChIP-Seq           GENOMIC  RANDOM            SRS004118                      Illumina Genome Analyzer II    22150965    3262293717   SRR067971     12793198         460555128


Obtaining detailed SRA metadata
===============================

::

    $ pysradb metadata SRP075720 --detailed | head

    study_accession experiment_accession experiment_title                                  experiment_desc                                   organism_taxid  organism_name library_strategy library_source  library_selection sample_accession sample_title instrument           total_spots total_size run_accession run_total_spots run_total_bases
    SRP075720       SRX1800476            GSM2177569: Kcng4_2la_H9; Mus musculus; RNA-Seq   GSM2177569: Kcng4_2la_H9; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467643                    Illumina HiSeq 2500  2547148      97658407  SRR3587912    2547148         127357400
    SRP075720       SRX1800475            GSM2177568: Kcng4_2la_H8; Mus musculus; RNA-Seq   GSM2177568: Kcng4_2la_H8; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467642                    Illumina HiSeq 2500  2676053     101904264  SRR3587911    2676053         133802650
    SRP075720       SRX1800474            GSM2177567: Kcng4_2la_H7; Mus musculus; RNA-Seq   GSM2177567: Kcng4_2la_H7; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467641                    Illumina HiSeq 2500  1603567      61729014  SRR3587910    1603567          80178350
    SRP075720       SRX1800473            GSM2177566: Kcng4_2la_H6; Mus musculus; RNA-Seq   GSM2177566: Kcng4_2la_H6; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467640                    Illumina HiSeq 2500  2498920      94977329  SRR3587909    2498920         124946000
    SRP075720       SRX1800472            GSM2177565: Kcng4_2la_H5; Mus musculus; RNA-Seq   GSM2177565: Kcng4_2la_H5; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467639                    Illumina HiSeq 2500  2226670      83473957  SRR3587908    2226670         111333500
    SRP075720       SRX1800471            GSM2177564: Kcng4_2la_H4; Mus musculus; RNA-Seq   GSM2177564: Kcng4_2la_H4; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467638                    Illumina HiSeq 2500  2269546      87486278  SRR3587907    2269546         113477300
    SRP075720       SRX1800470            GSM2177563: Kcng4_2la_H3; Mus musculus; RNA-Seq   GSM2177563: Kcng4_2la_H3; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467636                    Illumina HiSeq 2500  2333284      88669838  SRR3587906    2333284         116664200
    SRP075720       SRX1800469            GSM2177562: Kcng4_2la_H2; Mus musculus; RNA-Seq   GSM2177562: Kcng4_2la_H2; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467637                    Illumina HiSeq 2500  2071159      79689296  SRR3587905    2071159         103557950
    SRP075720       SRX1800468            GSM2177561: Kcng4_2la_H1; Mus musculus; RNA-Seq   GSM2177561: Kcng4_2la_H1; Mus musculus; RNA-Seq  10090           Mus musculus  RNA-Seq          TRANSCRIPTOMIC  cDNA              SRS1467635                    Illumina HiSeq 2500  2321657      89307894  SRR3587904    2321657         116082850



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


Downloading supplementary files from GEO
========================================

::

    $ pysradb download -g GSE161707
    

Downloading an entire SRA/ENA project (multithreaded)
=====================================================

``pysradb`` makes it super easy to download datasets from SRA parallely:
Using 8 threads to download:

::

    $ pysradb download -y -t 8 --out-dir ./pysradb_downloads -p SRP063852

Downloads are organized by ``SRP/SRX/SRR`` mimicking the hiererachy of SRA projects.


Downloading only certain samples of interest
============================================

::

    $ pysradb metadata SRP000941 --detailed | grep 'study\|RNA-Seq' | pysradb download

This will download all ``RNA-seq`` samples coming from this project.


Ultrafast fastq downloads
=========================

With `aspera-client <https://downloads.asperasoft.com/en/downloads/8?list>`_ installed, `pysradb` can perform ultra fast downloads:

To download all original fastqs with `aspera-client` installed utilizing 8 threads:

::

    $ pysradb download -t 8 --use_ascp -p SRP002605

Refer to the notebook for `(shallow) time benchmarks <https://colab.research.google.com/github/saketkc/pysradb/blob/master/notebooks/08.pysradb_ascp_multithreaded.ipynb>`_.




***********
Publication
***********

 `pysradb: A Python package to query next-generation sequencing metadata and data from NCBI Sequence Read Archive <https://f1000research.com/articles/8-532/v1>`_


 Presentation slides from BOSC (ISMB-ECCB) 2019: https://f1000research.com/slides/8-1183


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


**********
Questions?
**********

Join our `Slack Channel <https://join.slack.com/t/pysradb/shared_invite/zt-f01jndpy-KflPu3Be5Aq3FzRh5wj1Ug>`_ or open an `issue <https://github.com/saketkc/pysradb/issues>`_.

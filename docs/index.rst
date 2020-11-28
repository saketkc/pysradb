.. image:: _static/pysradb_v3.png

|

Welcome to pysradb's documentation!
======================================

============
Introduction
============

The NCBI Sequence Read Archive (SRA) is the primary archive of
next-generation sequencing datasets. SRA makes metadata and raw sequencing
data available to the research community to encourage reproducibility and
to provide avenues for testing novel hypotheses on publicly available data.

``pysradb`` provides a simple method to programmatically access metadata
and download sequencing data from SRA and European Bioinformatics
Institute's European Reads Archive (ENA).

.. code-block:: console

    $ pysradb metadata SRP265425
    study_accession experiment_accession    experiment_title        experiment_desc organism_taxid  organism_name   library_strategy        library_source  library_selection       sample_accession        sample_title    instrument      total_spots     total_size      run_accession   run_total_spots run_total_bases
    SRP265425       SRX8434255      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745319      Ion Torrent S5 XL       1311358 83306910       SRR11886735      1311358 109594216
    SRP265425       SRX8434254      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745320      Ion Torrent S5 XL       2614109 204278682      SRR11886736      2614109 262305651
    SRP265425       SRX8434253      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745318      Ion Torrent S5 XL       2286312 183516004      SRR11886737      2286312 263304134
    SRP265425       SRX8434252      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745317      Ion Torrent S5 XL       5202567 507524965      SRR11886738      5202567 781291588
    SRP265425       SRX8434251      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745315      Ion Torrent S5 XL       3313960 356104406      SRR11886739      3313960 612430817
    SRP265425       SRX8434250      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745316      Ion Torrent S5 XL       5155733 565882351      SRR11886740      5155733 954342917
    SRP265425       SRX8434249      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745313      Ion Torrent S5 XL       1324589 175619046      SRR11886741      1324589 216531400
    SRP265425       SRX8434248      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745314      Ion Torrent S5 XL       1639851 198973268      SRR11886742      1639851 245466005
    SRP265425       SRX8434247      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745312      Ion Torrent S5 XL       3921389 210198580      SRR11886743      3921389 332935558
    SRP265425       SRX8434246      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745311      Ion Torrent S5 XL       14295475        2150005008      SRR11886744     14295475        2967829315
    SRP265425       SRX8434245      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745310      Ion Torrent S5 XL       5124692 294846140      SRR11886745      5124692 431819462
    SRP265425       SRX8434244      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745309      Ion Torrent S5 XL       2986306 205666872      SRR11886746      2986306 275400959
    SRP265425       SRX8434243      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745308      Ion Torrent S5 XL       1182690 59471336       SRR11886747      1182690 86350631
    SRP265425       SRX8434242      Ampliseq of SARS-CoV-2  Ampliseq of SARS-CoV-2  2697049 Severe acute respiratory syndrome coronavirus 2 AMPLICON        VIRAL RNA       RT-PCR  SRS6745307      Ion Torrent S5 XL       6031816 749323230      SRR11886748      6031816 928054297


The strength of ``pysradb`` lies in its versatility: It can be used as
either a command-line application to easily retrieve the desired
information. It can also be used as a python package, which organises
metadata as `pandas` DataFrames, providing more control for data
exploration.

===========================================================================

============
Installation
============


Stable release
--------------

To install pysradb, run this command in your terminal:

.. code-block:: console

    $ pip install pysradb

This is the preferred method to install pysradb, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.


Alternatively, you may use conda:

.. code-block:: bash

   conda install -c bioconda pysradb

This step will install all the dependencies except aspera-client (which is not required, but highly recommended).
If you have an existing environment with a lot of pre-installed packages, conda might be `slow <https://github.com/bioconda/bioconda-recipes/issues/13774>`_.
Please consider creating a new enviroment for ``pysradb``:

.. code-block:: bash

   conda create -c bioconda -n pysradb PYTHON=3 pysradb


.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The source files for pysradb can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/saketkc/pysradb

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/saketkc/pysradb/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/saketkc/pysradb
.. _tarball: https://github.com/saketkc/pysradb/tarball/master

===========================================================================

=============
Using pysradb
=============

See :doc:`quickstart` to quickly get started using pysradb

Please see :doc:`usage_scenarios` for a few usage scenarios with detailed explanation.

===========================================================================

========
Contents
========

.. toctree::
   :maxdepth: 2

   quickstart
   cmdline
   python-api-usage
   usage_scenarios
   commands
   modules
   contributing
   authors
   history


===========================================================================


===========
Publication
===========

 `pysradb: A Python package to query next-generation sequencing metadata and data from NCBI Sequence Read Archive <https://f1000research.com/articles/8-532/v1>`_


 Presentation slides from BOSC (ISMB-ECCB) 2019: https://f1000research.com/slides/8-1183

===========================================================================

========
Citation
========

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

===========================================================================

==========
Questions?
==========

Join our `Slack Channel <https://join.slack.com/t/pysradb/shared_invite/zt-f01jndpy-KflPu3Be5Aq3FzRh5wj1Ug>`_ or open an `issue <https://github.com/saketkc/pysradb/issues>`_.

* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb


==================
Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. image:: _static/pysradb_v3.png

|

Welcome to pysradb's documentation!
======================================

============
Introduction
============

``pysradb`` simplifies downloading metadata and high-throughput sequencing
data from NCBI's Short Reads Archive (SRA) and EBI's European Reads Archive
(ENA) databases.

The strength of ``pysradb`` lies in its versatility: It can be used as
either a command-line application to easily retrieve the desired
information, or as a python package, which offers more control in terms of
data exploration.

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

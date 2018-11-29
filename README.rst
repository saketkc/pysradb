=======
pysradb
=======


.. image:: https://img.shields.io/pypi/v/pysradb.svg
        :target: https://pypi.python.org/pypi/pysradb

.. image:: https://img.shields.io/travis/saketkc/pysradb.svg
        :target: https://travis-ci.org/saketkc/pysradb

.. image:: https://readthedocs.org/projects/pysradb/badge/?version=latest
        :target: https://pysradb.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python package for interacting with SRAdb and downloading datasets from SRA.

Installation
------------

Dependecies
~~~~~~~~~~~

.. code-block:: bash
   
   pandas>=0.23.4
   click>=0.6
   aspera-client
   SRAmetadb.sqlite
   
SRAmetadb can be downloaded as:

.. code-block:: bash
    
   wget -c https://starbuck1.s3.amazonaws.com/sradb/SRAmetadb.sqlite.gz && gunzip SRAmetadb.sqlite.gz

`aspera-client` needs to be installed as well. Instructions are available here: https://downloads.asperasoft.com/connect2/



.. code-block:: bash

   pip install -U pandas click
   git clone https://github.com/saketkc/pysradb.git
   cd pysradb
   pip install -e .


Downloading data fron SRA
-------------------------

Downloading an entire project arranged experiment wise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   
   from pysradb import SRAdb
   db = SRAdb('SRAmetadb.sqlite')
   df = db.sra_convert('SRP017942')
   db.download(df)

Downloading a subset of experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   df = db.sra_convert('SRP000941')
   db.download(df=df_rna, out_dir='/pysradb_downloads')()



Features
--------

See Notebook: https://nbviewer.jupyter.org/github/saketkc/pysradb/blob/master/notebooks/demo.ipynb

* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb


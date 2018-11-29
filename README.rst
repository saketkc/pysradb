=======
pysradb
=======


.. image:: https://img.shields.io/pypi/v/pysradb.svg
        :target: https://pypi.python.org/pypi/pysradb

.. image:: https://travis-ci.com/saketkc/pysradb.svg?branch=master
        :target: https://travis-ci.com/saketkc/pysradb



Python package for interacting with SRAdb and downloading datasets from SRA.

Installation
------------

Dependecies
~~~~~~~~~~~

.. code-block:: bash

   pandas>=0.23.4
   click>=6.0
   tqdm>=4.28
   aspera-client
   SRAmetadb.sqlite

SRAmetadb can be downloaded as:

.. code-block:: bash

   wget -c https://starbuck1.s3.amazonaws.com/sradb/SRAmetadb.sqlite.gz && gunzip SRAmetadb.sqlite.gz

`aspera-client` needs to be installed as well. Instructions are available here: https://downloads.asperasoft.com/connect2/



.. code-block:: bash

   pip install -U pandas click tqdm
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


Demo
----

https://nbviewer.jupyter.org/github/saketkc/pysradb/blob/master/notebooks/demo.ipynb

* Free software: BSD license
* Documentation: https://saketkc.github.io/pysradb


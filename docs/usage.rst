=====
Usage
=====

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


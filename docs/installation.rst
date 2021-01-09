.. _installation:

############
Installation
############

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





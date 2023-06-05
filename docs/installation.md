# Installation

## Stable release

To install pysradb, run this command in your terminal:

``` console
$ pip install pysradb
```

This is the preferred method to install pysradb, as it will always
install the most recent stable release.

If you don\'t have [pip](https://pip.pypa.io) installed, this [Python
installation
guide](http://docs.python-guide.org/en/latest/starting/installation/)
can guide you through the process.

Alternatively, you may use conda:

``` bash
conda install -c bioconda pysradb
```

This step will install all the dependencies except aspera-client (which
is not required, but highly recommended). If you have an existing
environment with a lot of pre-installed packages, conda might be
[slow](https://github.com/bioconda/bioconda-recipes/issues/13774).
Please consider creating a new enviroment for `pysradb`:

``` bash
conda create -c bioconda -n pysradb PYTHON=3 pysradb
```

## From sources

The source files for pysradb can be downloaded from the [Github
repo](https://github.com/saketkc/pysradb).

You can either clone the public repository:

``` console
$ git clone git://github.com/saketkc/pysradb
```

Or download the
[tarball](https://github.com/saketkc/pysradb/tarball/master):

``` console
$ curl  -OL https://github.com/saketkc/pysradb/tarball/master
```

Once you have a copy of the source, you can install it with:

``` console
$ python setup.py install
```

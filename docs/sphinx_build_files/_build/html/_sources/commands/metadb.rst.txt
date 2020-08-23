.. _metadb:

######
metadb
######

``metadb`` downloads `SRAmetadb.sqlite` file provided by the ``SRAdb`` project.

=================
Usage and options
=================

::

    $ pysradb metadb -h

    Usage: pysradb metadb [OPTIONS]

      Download SRAmetadb.sqlite

    Options:
      --out-dir TEXT       Output directory location
      --overwrite BOOLEAN  Overwrite existing file
      -h, --help           Show this message and exit.


By default ``metadb`` command will download the file in the current
working directory. Please be patient, since the download and unzipping
operations can be potentially slow. There are progress bars at each
step that give an estimated time of completion.


You can specify a different directory for download by ``--out-dir`` argument:

::

    $ pysradb metadb --out-dir /path/to/my_data

If ``SRAmetadb.sqlite`` already exists in the current directory
or at the location specified by ``--out-dir``, ``pysradb`` will NOT
overwrite it, unless explicitly asked to via the ``--overwrite`` flag.





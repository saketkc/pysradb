.. _srametadata:

############
metadata
############

``metadata`` outputs a metatable for a SRA study accession (SRP).

=================
Usage and options
=================

::

    $ pysrab metadata -h

    Usage: pysradb metadata [OPTIONS] SRP_ID

      Fetch metadata for SRA project (SRPnnnn)

    Options:
      --saveto TEXT  Save metadata dataframe to file
      --detailed     Display detailed metadata table
      -h, --help     Show this message and exit.


==========================================================
Obtaining  metadata for SRA study accession (SRP metadata)
==========================================================


To obtain concise metadata for a SRP ID, we can use ``metadata``.
The default metadata returned includes:

- experiment accession (SRX)
- sample accession (SRS)
- run accession (SRR)

::

    $ pysradb metadata SRP026005

    study_accession experiment_accession sample_accession run_accession
    SRP026005       SRX305245            SRS444476        SRR900108
    SRP026005       SRX305246            SRS444467        SRR900109
    SRP026005       SRX305247            SRS444468        SRR900110
    SRP026005       SRX305247            SRS444468        SRR900111
    SRP026005       SRX305248            SRS444470        SRR900112
    SRP026005       SRX305249            SRS444471        SRR900113
    SRP026005       SRX305250            SRS444472        SRR900114
    SRP026005       SRX305250            SRS444472        SRR900115
    SRP026005       SRX305251            SRS444473        SRR900116
    SRP026005       SRX305251            SRS444473        SRR900117
    SRP026005       SRX305252            SRS444474        SRR900118
    SRP026005       SRX305252            SRS444474        SRR900119
    SRP026005       SRX305253            SRS444475        SRR900120
    SRP026005       SRX305253            SRS444475        SRR900121


In order to subset only ``RNA-seq`` experiments, you can do this simple operation:

::

    $ pysradb metadata SRP098789 --detailed| grep 'study|RNA-Seq'




==============================
Getting more detailed metadata
==============================

A major chunk of metadata information is still hidden by default.
For example, how long are the reads for each experiment?
Is the sequencing run single end or paired end?
Detailed metadata can be obtained by adding the ``--detailed``
flag:


::

    $ pysradb metadata SRP098789 --detailed



=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb metadata --detailed --saveto SRP098789_metadata.tsv SRP098789

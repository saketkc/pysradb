.. _gsetosrp:

##########
gse-to-srp
##########

``gse-to-srp`` converts a GEO accession ID (GSE) to SRA
study accession (SRP).

=================
Usage and options
=================

::

    $ pysradb gse-to-srp -h

    Usage: pysradb gse-to-srp [OPTIONS] GSE_IDS...

      Get SRP for a GSE

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [experiment_accession (SRX),
                                                 sample_accession (SRS),
                                                 experiment_alias (GSM_),
                                                 sample_alias (GSM)]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


===========================================================
Convert GEO accession ID (GSE) to SRA study accession (SRP)
===========================================================

Gene Expression Omnibus or GEO hosts processed sequencing datasets.
The raw data is available through SRA and hence we often need to
interpolate between the two.

To convert a GEO experiment with ID of the form ``GSEnnnn`` to
its corresponding SRA study accession of the form ``SRPmmmmm``:

::

    $ pysradb gse-to-srp GSE41637

    study_alias study_accession
    GSE41637    SRP016501

=========================
Getting sample attributes
=========================

Often, the most useful information is in the ``sample_attribute``
column of ``SRAmetadb``. For example, what cell` types do
different experiments correspond to? What treatments have been
applied to them? This can be listed by using the ``-desc``
tag. Note however that, this will not however any accessions
related to the experiment or run. You will need the ``--detailed``
tag if you want the sample/run/experiment accessions.


::

    $ pysradb gse-to-srp --desc GSE41637

    study_alias study_accession sample_attribute
    GSE41637    SRP016501       source_name: chicken_brain || tissue: brain
    GSE41637    SRP016501       source_name: chicken_colon || tissue: colon
    GSE41637    SRP016501       source_name: chicken_heart || tissue: heart
    GSE41637    SRP016501       source_name: chicken_kidney || tissue: kidney
    GSE41637    SRP016501       source_name: chicken_liver || tissue: liver
    GSE41637    SRP016501       source_name: chicken_lung || tissue: lung
    GSE41637    SRP016501       source_name: chicken_skm || tissue: skeletal muscle
    GSE41637    SRP016501       source_name: chicken_spleen || tissue: spleen
    GSE41637    SRP016501       source_name: chicken_testes || tissue: testes


But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb gse-to-srp --detailed --desc GSE41637

    study_alias study_accession experiment_accession sample_accession experiment_alias sample_alias sample_attribute
    GSE41637    SRP016501       SRX196264            SRS369701        GSM1020640_1     GSM1020640   source_name: mouse_brain || strain: DBA/2J || tissue: brain
    GSE41637    SRP016501       SRX196265            SRS369702        GSM1020641_1     GSM1020641   source_name: mouse_colon || strain: DBA/2J || tissue: colon
    GSE41637    SRP016501       SRX196266            SRS369703        GSM1020642_1     GSM1020642   source_name: mouse_heart || strain: DBA/2J || tissue: heart
    GSE41637    SRP016501       SRX196267            SRS369704        GSM1020643_1     GSM1020643   source_name: mouse_kidney || strain: DBA/2J || tissue: kidney
    GSE41637    SRP016501       SRX196268            SRS369705        GSM1020644_1     GSM1020644   source_name: mouse_liver || strain: DBA/2J || tissue: liver
    GSE41637    SRP016501       SRX196269            SRS369706        GSM1020645_1     GSM1020645   source_name: mouse_lung || strain: DBA/2J || tissue: lung
    GSE41637    SRP016501       SRX196270            SRS369707        GSM1020646_1     GSM1020646   source_name: mouse_skm || strain: DBA/2J || tissue: skeletal muscle
    GSE41637    SRP016501       SRX196271            SRS369708        GSM1020647_1     GSM1020647   source_name: mouse_spleen || strain: DBA/2J || tissue: spleen
    GSE41637    SRP016501       SRX196272            SRS369709        GSM1020648_1     GSM1020648   source_name: mouse_testes || strain: DBA/2J || tissue: testes


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb gse-to-srp --detailed --desc --expand GSE41637

    study_alias study_accession experiment_accession sample_accession experiment_alias sample_alias source_name     strain          tissue
    GSE41637    SRP016501       SRX196264            SRS369701        GSM1020640_1     GSM1020640   mouse_brain     dba/2j          brain
    GSE41637    SRP016501       SRX196265            SRS369702        GSM1020641_1     GSM1020641   mouse_colon     dba/2j          colon
    GSE41637    SRP016501       SRX196266            SRS369703        GSM1020642_1     GSM1020642   mouse_heart     dba/2j          heart
    GSE41637    SRP016501       SRX196267            SRS369704        GSM1020643_1     GSM1020643   mouse_kidney    dba/2j          kidney
    GSE41637    SRP016501       SRX196268            SRS369705        GSM1020644_1     GSM1020644   mouse_liver     dba/2j          liver
    GSE41637    SRP016501       SRX196269            SRS369706        GSM1020645_1     GSM1020645   mouse_lung      dba/2j          lung
    GSE41637    SRP016501       SRX196270            SRS369707        GSM1020646_1     GSM1020646   mouse_skm       dba/2j          skeletal muscle
    GSE41637    SRP016501       SRX196271            SRS369708        GSM1020647_1     GSM1020647   mouse_spleen    dba/2j          spleen
    GSE41637    SRP016501       SRX196272            SRS369709        GSM1020648_1     GSM1020648   mouse_testes    dba/2j          testes



=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb gse-to-srp --detailed --expand --saveto GSE41637_metadata.tsv GSE41637

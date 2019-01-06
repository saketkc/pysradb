.. _gsetogsm:

##########
gse-to-gsm
##########

``gse-to-gsm`` provides list of GEO experiments (GSM) for a GEO study accession (GSE).

=================
Usage and options
=================

::


    $ pysradb gse-to-gsm

    Usage: pysradb gse-to-gsm [OPTIONS] GSE_IDS...

      Get SRP for a GSE

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [sample_accession, run_accession]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.



==============================================================
Convert GEO accesion ID (GSE) to GEO expriment accession (GSM)
==============================================================

Getting GSMs from GSE is straight forward:

::

    $ pysradb gse-to-gsm GSE41637 | head

    study_alias experiment_alias
    GSE41637    GSM1020640_1
    GSE41637    GSM1020641_1
    GSE41637    GSM1020642_1
    GSE41637    GSM1020643_1
    GSE41637    GSM1020644_1
    GSE41637    GSM1020645_1
    GSE41637    GSM1020646_1
    GSE41637    GSM1020647_1
    GSE41637    GSM1020648_1



=========================
Getting sample attributes
=========================

Often, the most useful information is in the ``sample_attribute``
column of ``SRAmetadb``. For example, what cell` types do
different experiments correspond to? What treatments have been
applied to them? This can be listed by using the ``-desc``
tag. Note however that, this will not however any accesions
related to the experiment or run. You will need the ``--detailed``
tag if you want the sample/run/experiment accesions.


::

    $ pysradb gse-to-gsm --desc GSE41637

    study_alias experiment_alias sample_attribute
    GSE41637    GSM1020640_1     source_name: mouse_brain || strain: DBA/2J || tissue: brain
    GSE41637    GSM1020641_1     source_name: mouse_colon || strain: DBA/2J || tissue: colon
    GSE41637    GSM1020642_1     source_name: mouse_heart || strain: DBA/2J || tissue: heart
    GSE41637    GSM1020643_1     source_name: mouse_kidney || strain: DBA/2J || tissue: kidney
    GSE41637    GSM1020644_1     source_name: mouse_liver || strain: DBA/2J || tissue: liver
    GSE41637    GSM1020645_1     source_name: mouse_lung || strain: DBA/2J || tissue: lung
    GSE41637    GSM1020646_1     source_name: mouse_skm || strain: DBA/2J || tissue: skeletal muscle
    GSE41637    GSM1020647_1     source_name: mouse_spleen || strain: DBA/2J || tissue: spleen
    GSE41637    GSM1020648_1     source_name: mouse_testes || strain: DBA/2J || tissue: testes

But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb gse-to-gsm --detailed --desc GSE41637

    study_alias experiment_alias source_name     strain          tissue
    GSE41637    GSM1020640_1     mouse_brain     dba/2j          brain
    GSE41637    GSM1020641_1     mouse_colon     dba/2j          colon
    GSE41637    GSM1020642_1     mouse_heart     dba/2j          heart
    GSE41637    GSM1020643_1     mouse_kidney    dba/2j          kidney
    GSE41637    GSM1020644_1     mouse_liver     dba/2j          liver
    GSE41637    GSM1020645_1     mouse_lung      dba/2j          lung
    GSE41637    GSM1020646_1     mouse_skm       dba/2j          skeletal muscle
    GSE41637    GSM1020647_1     mouse_spleen    dba/2j          spleen
    GSE41637    GSM1020648_1     mouse_testes    dba/2j          testes


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb gse-to-gsm --desc --expand GSE41637

    study_alias experiment_alias source_name     strain          tissue
    GSE41637    GSM1020640_1     mouse_brain     dba/2j          brain
    GSE41637    GSM1020641_1     mouse_colon     dba/2j          colon
    GSE41637    GSM1020642_1     mouse_heart     dba/2j          heart
    GSE41637    GSM1020643_1     mouse_kidney    dba/2j          kidney
    GSE41637    GSM1020644_1     mouse_liver     dba/2j          liver
    GSE41637    GSM1020645_1     mouse_lung      dba/2j          lung
    GSE41637    GSM1020646_1     mouse_skm       dba/2j          skeletal muscle




=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``saveto`` argument:

::

    $ pysradb gse-to-gsm --detailed --expand --saveto GSE41637_metadata.tsv GSE41637


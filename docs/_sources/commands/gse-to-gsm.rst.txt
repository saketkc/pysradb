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
      --detailed     Output additional columns: [sample_accession (SRS),
                                                 run_accession (SRR),
                                                 sample_alias (GSM),
                                                 run_alias (GSM_r)]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.



===============================================================
Convert GEO accession ID (GSE) to GEO expriment accession (GSM)
===============================================================

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
tag. Note however that, this will not however any accessions
related to the experiment or run. You will need the ``--detailed``
tag if you want the sample/run/experiment accessions.


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


But without the context of individual experiment and run accessions, this information
is not so useful. The ``--detailed`` flag outputs additional columns:

- sample_accession (SRS)
- run_accession (SRR)
- sample_alias (GSM)
- run_alias (GSM_r)

::

    $ pysradb gse-to-gsm --detailed --desc GSE41637

    study_alias experiment_alias experiment_accession sample_accession run_accession sample_alias run_alias      sample_attribute
    GSE41637    GSM1020640_1     SRX196264            SRS369701        SRR594393     GSM1020640   GSM1020640_r1  source_name: mouse_brain || strain: DBA/2J || tissue: brain
    GSE41637    GSM1020641_1     SRX196265            SRS369702        SRR594394     GSM1020641   GSM1020641_r1  source_name: mouse_colon || strain: DBA/2J || tissue: colon
    GSE41637    GSM1020642_1     SRX196266            SRS369703        SRR594395     GSM1020642   GSM1020642_r1  source_name: mouse_heart || strain: DBA/2J || tissue: heart
    GSE41637    GSM1020643_1     SRX196267            SRS369704        SRR594396     GSM1020643   GSM1020643_r1  source_name: mouse_kidney || strain: DBA/2J || tissue: kidney
    GSE41637    GSM1020644_1     SRX196268            SRS369705        SRR594397     GSM1020644   GSM1020644_r1  source_name: mouse_liver || strain: DBA/2J || tissue: liver
    GSE41637    GSM1020645_1     SRX196269            SRS369706        SRR594398     GSM1020645   GSM1020645_r1  source_name: mouse_lung || strain: DBA/2J || tissue: lung
    GSE41637    GSM1020646_1     SRX196270            SRS369707        SRR594399     GSM1020646   GSM1020646_r1  source_name: mouse_skm || strain: DBA/2J || tissue: skeletal muscle
    GSE41637    GSM1020647_1     SRX196271            SRS369708        SRR594400     GSM1020647   GSM1020647_r1  source_name: mouse_spleen || strain: DBA/2J || tissue: spleen
    GSE41637    GSM1020648_1     SRX196272            SRS369709        SRR594401     GSM1020648   GSM1020648_r1  source_name: mouse_testes || strain: DBA/2J || tissue: testes


Using ``--expand`` flag alongside:

::

    $ pysradb gse-to-gsm --detailed --desc --expand GSE41637
    study_alias experiment_alias experiment_accession sample_accession run_accession sample_alias run_alias      source_name     strain          tissue
    GSE41637    GSM1020640_1     SRX196264            SRS369701        SRR594393     GSM1020640   GSM1020640_r1  mouse_brain     dba/2j          brain
    GSE41637    GSM1020641_1     SRX196265            SRS369702        SRR594394     GSM1020641   GSM1020641_r1  mouse_colon     dba/2j          colon
    GSE41637    GSM1020642_1     SRX196266            SRS369703        SRR594395     GSM1020642   GSM1020642_r1  mouse_heart     dba/2j          heart
    GSE41637    GSM1020643_1     SRX196267            SRS369704        SRR594396     GSM1020643   GSM1020643_r1  mouse_kidney    dba/2j          kidney
    GSE41637    GSM1020644_1     SRX196268            SRS369705        SRR594397     GSM1020644   GSM1020644_r1  mouse_liver     dba/2j          liver
    GSE41637    GSM1020645_1     SRX196269            SRS369706        SRR594398     GSM1020645   GSM1020645_r1  mouse_lung      dba/2j          lung
    GSE41637    GSM1020646_1     SRX196270            SRS369707        SRR594399     GSM1020646   GSM1020646_r1  mouse_skm       dba/2j          skeletal muscle
    GSE41637    GSM1020647_1     SRX196271            SRS369708        SRR594400     GSM1020647   GSM1020647_r1  mouse_spleen    dba/2j          spleen
    GSE41637    GSM1020648_1     SRX196272            SRS369709        SRR594401     GSM1020648   GSM1020648_r1  mouse_testes    dba/2j          testes


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb gse-to-gsm --detailed --expand --saveto GSE41637_metadata.tsv GSE41637


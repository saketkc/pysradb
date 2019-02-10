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
      --db FILE      Path to SRAmetadb.sqlite file
      --assay        Include assay type in output
      --desc         Should sample_attribute be included
      --detailed     Display detailed metadata table
      --expand       Should sample_attribute be expanded
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


========================
Getting library strategy
========================

The metadata information above, by itself is not everything that we are
often looking for. Each study can have different libraries. We might
be interested only in the ``RNA-seq`` libraries. A new column
indicating the library strategy can be added to the output by
specifying ``--assay`` flag.

::

    $ pysradb metadata SRP098789 --assay | grep 'study|RNA-Seq'

    study_accession experiment_accession sample_accession run_accession library_strategy
    SRP098789       SRX2536403           SRS1956353       SRR5227288    OTHER
    SRP098789       SRX2536404           SRS1956354       SRR5227289    OTHER
    SRP098789       SRX2536405           SRS1956355       SRR5227290    OTHER
    SRP098789       SRX2536406           SRS1956356       SRR5227291    OTHER
    SRP098789       SRX2536407           SRS1956357       SRR5227292    OTHER
    SRP098789       SRX2536408           SRS1956358       SRR5227293    OTHER
    SRP098789       SRX2536409           SRS1956359       SRR5227294    OTHER
    SRP098789       SRX2536410           SRS1956360       SRR5227295    OTHER
    SRP098789       SRX2536411           SRS1956361       SRR5227296    OTHER
    SRP098789       SRX2536412           SRS1956362       SRR5227297    OTHER
    SRP098789       SRX2536413           SRS1956363       SRR5227298    OTHER
    SRP098789       SRX2536414           SRS1956364       SRR5227299    OTHER
    SRP098789       SRX2536415           SRS1956365       SRR5227300    OTHER
    SRP098789       SRX2536416           SRS1956366       SRR5227301    OTHER
    SRP098789       SRX2536417           SRS1956367       SRR5227302    OTHER
    SRP098789       SRX2536418           SRS1956368       SRR5227303    OTHER
    SRP098789       SRX2536419           SRS1956369       SRR5227304    OTHER
    SRP098789       SRX2536420           SRS1956370       SRR5227305    OTHER
    SRP098789       SRX2536421           SRS1956371       SRR5227306    OTHER
    SRP098789       SRX2536422           SRS1956372       SRR5227307    RNA-Seq
    SRP098789       SRX2536423           SRS1956373       SRR5227308    OTHER
    SRP098789       SRX2536424           SRS1956374       SRR5227309    RNA-Seq
    SRP098789       SRX2536425           SRS1956375       SRR5227310    OTHER
    SRP098789       SRX2536426           SRS1956376       SRR5227311    RNA-Seq
    SRP098789       SRX2536427           SRS1956377       SRR5227312    OTHER
    SRP098789       SRX2536428           SRS1956378       SRR5227313    RNA-Seq


In order to subset only ``RNA-seq`` experiments, you can do this simple operation:

::

    $ pysradb metadata SRP098789 --assay | grep 'study|RNA-Seq'


========================================
Getting sample and experiment attributes
========================================

A major chunk of informative metadata is hidden in
the ``sample_attribute`` column.
For example, what cell types or conditions does
each of the experiment involve? If this was a time course
study, which expriments correspond to which?
To add the ``sample_attribute`` column to the output
table, we need the ``--desc`` tag:

::

    $ pysradb metadata --desc SRP098789

    study_accession experiment_accession sample_accession run_accession sample_attribute
    SRP098789       SRX2536403           SRS1956353       SRR5227288    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536404           SRS1956354       SRR5227289    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536405           SRS1956355       SRR5227290    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536406           SRS1956356       SRR5227291    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536407           SRS1956357       SRR5227292    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536408           SRS1956358       SRR5227293    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536409           SRS1956359       SRR5227294    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536410           SRS1956360       SRR5227295    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536411           SRS1956361       SRR5227296    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536412           SRS1956362       SRR5227297    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536413           SRS1956363       SRR5227298    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536414           SRS1956364       SRR5227299    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536415           SRS1956365       SRR5227300    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536416           SRS1956366       SRR5227301    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536417           SRS1956367       SRR5227302    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536418           SRS1956368       SRR5227303    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536419           SRS1956369       SRR5227304    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536420           SRS1956370       SRR5227305    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536421           SRS1956371       SRR5227306    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536422           SRS1956372       SRR5227307    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRX2536423           SRS1956373       SRR5227308    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536424           SRS1956374       SRR5227309    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRX2536425           SRS1956375       SRR5227310    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536426           SRS1956376       SRR5227311    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRX2536427           SRS1956377       SRR5227312    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRX2536428           SRS1956378       SRR5227313    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb metadata --desc --expand SRP098789

    study_accession experiment_accession sample_accession run_accession cell_line library_type source_name                                  treatment_time
    SRP098789       SRX2536403           SRS1956353       SRR5227288    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536404           SRS1956354       SRR5227289    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536405           SRS1956355       SRR5227290    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536406           SRS1956356       SRR5227291    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536407           SRS1956357       SRR5227292    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536408           SRS1956358       SRR5227293    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536409           SRS1956359       SRR5227294    huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRX2536410           SRS1956360       SRR5227295    huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRX2536411           SRS1956361       SRR5227296    huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRX2536412           SRS1956362       SRR5227297    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536413           SRS1956363       SRR5227298    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536414           SRS1956364       SRR5227299    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536415           SRS1956365       SRR5227300    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536416           SRS1956366       SRR5227301    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536417           SRS1956367       SRR5227302    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536418           SRS1956368       SRR5227303    huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536419           SRS1956369       SRR5227304    huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536420           SRS1956370       SRR5227305    huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536421           SRS1956371       SRR5227306    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536422           SRS1956372       SRR5227307    huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       SRX2536423           SRS1956373       SRR5227308    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536424           SRS1956374       SRR5227309    huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       SRX2536425           SRS1956375       SRR5227310    huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536426           SRS1956376       SRR5227311    huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min
    SRP098789       SRX2536427           SRS1956377       SRR5227312    huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536428           SRS1956378       SRR5227313    huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min




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

    study_accession experiment_accession sample_accession run_accession experiment_title                                                                  experiment_attribute       sample_attribute                                                                                                                  taxon_id library_selection library_layout library_strategy library_source  library_name  bases       spots    adapter_spec  avg_read_length
    SRP098789       SRX2536403           SRS1956353       SRR5227288    GSM2475997: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2475997  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2104142750  42082855  None         50.0
    SRP098789       SRX2536404           SRS1956354       SRR5227289    GSM2475998: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2475998  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2082873050  41657461  None         50.0
    SRP098789       SRX2536405           SRS1956355       SRR5227290    GSM2475999: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2475999  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2023148650  40462973  None         50.0
    SRP098789       SRX2536406           SRS1956356       SRR5227291    GSM2476000: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2476000  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2057165950  41143319  None         50.0
    SRP098789       SRX2536407           SRS1956357       SRR5227292    GSM2476001: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2476001  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3027621850  60552437  None         50.0
    SRP098789       SRX2536408           SRS1956358       SRR5227293    GSM2476002: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2476002  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2135456900  42709138  None         50.0
    SRP098789       SRX2536409           SRS1956359       SRR5227294    GSM2476003: vehicle, 10 min rep 1; Homo sapiens; OTHER                            GEO Accession: GSM2476003  source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3800106100  76002122  None         50.0
    SRP098789       SRX2536410           SRS1956360       SRR5227295    GSM2476004: vehicle, 10 min rep 2; Homo sapiens; OTHER                            GEO Accession: GSM2476004  source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2306857400  46137148  None         50.0
    SRP098789       SRX2536411           SRS1956361       SRR5227296    GSM2476005: vehicle, 10 min rep 3; Homo sapiens; OTHER                            GEO Accession: GSM2476005  source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2636889200  52737784  None         50.0
    SRP098789       SRX2536412           SRS1956362       SRR5227297    GSM2476006: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2476006  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3019068250  60381365  None         50.0
    SRP098789       SRX2536413           SRS1956363       SRR5227298    GSM2476007: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2476007  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2466719600  49334392  None         50.0
    SRP098789       SRX2536414           SRS1956364       SRR5227299    GSM2476008: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2476008  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2438310650  48766213  None         50.0
    SRP098789       SRX2536415           SRS1956365       SRR5227300    GSM2476009: 0.3 Ã‚ÂµM PF-067446846, 60 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2476009  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         1502168100  30043362  None         50.0
    SRP098789       SRX2536416           SRS1956366       SRR5227301    GSM2476010: 0.3 Ã‚ÂµM PF-067446846, 60 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2476010  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2456475600  49129512  None         50.0
    SRP098789       SRX2536417           SRS1956367       SRR5227302    GSM2476011: 0.3 Ã‚ÂµM PF-067446846, 60 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2476011  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2212909000  44258180  None         50.0
    SRP098789       SRX2536418           SRS1956368       SRR5227303    GSM2476012: vehicle, 60 min rep 1; Homo sapiens; OTHER                            GEO Accession: GSM2476012  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2547808900  50956178  None         50.0
    SRP098789       SRX2536419           SRS1956369       SRR5227304    GSM2476013: vehicle, 60 min rep 2; Homo sapiens; OTHER                            GEO Accession: GSM2476013  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2356952850  47139057  None         50.0
    SRP098789       SRX2536420           SRS1956370       SRR5227305    GSM2476014: vehicle, 60 min rep 3; Homo sapiens; OTHER                            GEO Accession: GSM2476014  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2420251700  48405034  None         50.0
    SRP098789       SRX2536421           SRS1956371       SRR5227306    GSM2476015: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 4 -riboseq; Homo sapiens; OTHER   GEO Accession: GSM2476015  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2936988765  57588015  None         51.0
    SRP098789       SRX2536422           SRS1956372       SRR5227307    GSM2476016: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 4-mRNAseq; Homo sapiens; RNA-Seq  GEO Accession: GSM2476016  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq  9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         3390530541  66480991  None         51.0
    SRP098789       SRX2536423           SRS1956373       SRR5227308    GSM2476017: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 5 -riboseq; Homo sapiens; OTHER   GEO Accession: GSM2476017  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3345152067  65591217  None         51.0
    SRP098789       SRX2536424           SRS1956374       SRR5227309    GSM2476018: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 5-mRNAseq; Homo sapiens; RNA-Seq  GEO Accession: GSM2476018  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq  9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         2043193263  40062613  None         51.0
    SRP098789       SRX2536425           SRS1956375       SRR5227310    GSM2476019: vehicle, 60 min, rep 4 -riboseq; Homo sapiens; OTHER                  GEO Accession: GSM2476019  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3384542835  66363585  None         51.0
    SRP098789       SRX2536426           SRS1956376       SRR5227311    GSM2476020: vehicle, 60 min, rep 4-mRNAseq; Homo sapiens; RNA-Seq                 GEO Accession: GSM2476020  source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq                 9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         3249730455  63720205  None         51.0
    SRP098789       SRX2536427           SRS1956377       SRR5227312    GSM2476021: vehicle, 60 min, rep 5 -riboseq; Homo sapiens; OTHER                  GEO Accession: GSM2476021  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2961321834  58065134  None         51.0
    SRP098789       SRX2536428           SRS1956378       SRR5227313    GSM2476022: vehicle, 60 min, rep 5-mRNAseq; Homo sapiens; RNA-Seq                 GEO Accession: GSM2476022  source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq                 9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         3540569481  69422931  None         51.0



Again, in order to expand the ``sample_attribute`` column,
we can make use of the ``--expand`` tag:

::

    $ pysradb metadata --detailed --expand SRP098789

    study_accession experiment_accession sample_accession run_accession experiment_title                                                                  experiment_attribute        taxon_id library_selection library_layout library_strategy library_source  library_name  bases       spots    adapter_spec  avg_read_length cell_line library_type source_name                                  treatment_time
    SRP098789       SRX2536403           SRS1956353       SRR5227288    GSM2475997: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2475997  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2104142750  42082855  None         50.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536404           SRS1956354       SRR5227289    GSM2475998: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2475998  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2082873050  41657461  None         50.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536405           SRS1956355       SRR5227290    GSM2475999: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2475999  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2023148650  40462973  None         50.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536406           SRS1956356       SRR5227291    GSM2476000: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2476000  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2057165950  41143319  None         50.0             huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536407           SRS1956357       SRR5227292    GSM2476001: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2476001  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3027621850  60552437  None         50.0             huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536408           SRS1956358       SRR5227293    GSM2476002: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2476002  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2135456900  42709138  None         50.0             huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRX2536409           SRS1956359       SRR5227294    GSM2476003: vehicle, 10 min rep 1; Homo sapiens; OTHER                            GEO Accession: GSM2476003  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3800106100  76002122  None         50.0             huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRX2536410           SRS1956360       SRR5227295    GSM2476004: vehicle, 10 min rep 2; Homo sapiens; OTHER                            GEO Accession: GSM2476004  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2306857400  46137148  None         50.0             huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRX2536411           SRS1956361       SRR5227296    GSM2476005: vehicle, 10 min rep 3; Homo sapiens; OTHER                            GEO Accession: GSM2476005  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2636889200  52737784  None         50.0             huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRX2536412           SRS1956362       SRR5227297    GSM2476006: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2476006  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3019068250  60381365  None         50.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536413           SRS1956363       SRR5227298    GSM2476007: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2476007  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2466719600  49334392  None         50.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536414           SRS1956364       SRR5227299    GSM2476008: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2476008  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2438310650  48766213  None         50.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536415           SRS1956365       SRR5227300    GSM2476009: 0.3 Ã‚ÂµM PF-067446846, 60 min, rep 1; Homo sapiens; OTHER            GEO Accession: GSM2476009  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         1502168100  30043362  None         50.0             huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536416           SRS1956366       SRR5227301    GSM2476010: 0.3 Ã‚ÂµM PF-067446846, 60 min, rep 2; Homo sapiens; OTHER            GEO Accession: GSM2476010  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2456475600  49129512  None         50.0             huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536417           SRS1956367       SRR5227302    GSM2476011: 0.3 Ã‚ÂµM PF-067446846, 60 min, rep 3; Homo sapiens; OTHER            GEO Accession: GSM2476011  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2212909000  44258180  None         50.0             huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536418           SRS1956368       SRR5227303    GSM2476012: vehicle, 60 min rep 1; Homo sapiens; OTHER                            GEO Accession: GSM2476012  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2547808900  50956178  None         50.0             huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536419           SRS1956369       SRR5227304    GSM2476013: vehicle, 60 min rep 2; Homo sapiens; OTHER                            GEO Accession: GSM2476013  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2356952850  47139057  None         50.0             huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536420           SRS1956370       SRR5227305    GSM2476014: vehicle, 60 min rep 3; Homo sapiens; OTHER                            GEO Accession: GSM2476014  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2420251700  48405034  None         50.0             huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536421           SRS1956371       SRR5227306    GSM2476015: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 4 -riboseq; Homo sapiens; OTHER   GEO Accession: GSM2476015  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2936988765  57588015  None         51.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536422           SRS1956372       SRR5227307    GSM2476016: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 4-mRNAseq; Homo sapiens; RNA-Seq  GEO Accession: GSM2476016  9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         3390530541  66480991  None         51.0             huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       SRX2536423           SRS1956373       SRR5227308    GSM2476017: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 5 -riboseq; Homo sapiens; OTHER   GEO Accession: GSM2476017  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3345152067  65591217  None         51.0             huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRX2536424           SRS1956374       SRR5227309    GSM2476018: 1.5 Ã‚ÂµM PF-067446846, 60 min, rep 5-mRNAseq; Homo sapiens; RNA-Seq  GEO Accession: GSM2476018  9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         2043193263  40062613  None         51.0             huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       SRX2536425           SRS1956375       SRR5227310    GSM2476019: vehicle, 60 min, rep 4 -riboseq; Homo sapiens; OTHER                  GEO Accession: GSM2476019  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         3384542835  66363585  None         51.0             huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536426           SRS1956376       SRR5227311    GSM2476020: vehicle, 60 min, rep 4-mRNAseq; Homo sapiens; RNA-Seq                 GEO Accession: GSM2476020  9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         3249730455  63720205  None         51.0             huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min
    SRP098789       SRX2536427           SRS1956377       SRR5227312    GSM2476021: vehicle, 60 min, rep 5 -riboseq; Homo sapiens; OTHER                  GEO Accession: GSM2476021  9606      other             SINGLE -       OTHER            TRANSCRIPTOMIC  None         2961321834  58065134  None         51.0             huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRX2536428           SRS1956378       SRR5227313    GSM2476022: vehicle, 60 min, rep 5-mRNAseq; Homo sapiens; RNA-Seq                 GEO Accession: GSM2476022  9606      cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         3540569481  69422931  None         51.0             huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb metadata --detailed --expand --saveto SRP098789_metadata.tsv SRP098789

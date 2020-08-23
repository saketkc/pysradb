.. _srptosrr:

##########
srp-to-srr
##########

``srp-to-srr`` converts a SRA study accession (SRP) to corresponding
SRA run accession(s) (SRR).

=================
Usage and options
=================

::


    $ pysradb srp-to-srr -h

    Usage: pysradb srp-to-srr [OPTIONS] SRP_ID

      Get SRR for a SRP

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [experiment_accession (SRX),
                                                 sample_accession (SRS),
                                                 study_alias (GSE),
                                                 experiment_alias (GSM),
                                                 sample_alias (GSM_),
                                                 run_alias (GSM_r)],
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


===============================================================
Convert SRA study accession (SRP) to SRA run accession(s) (SRR)
===============================================================

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding SRA run accessions of the form ``SRRnnnn``:

::

    $ pysradb srp-to-srr SRP098789

    study_accession run_accession
    SRP098789       SRR5227288
    SRP098789       SRR5227289
    SRP098789       SRR5227290
    SRP098789       SRR5227291
    SRP098789       SRR5227292
    SRP098789       SRR5227293
    SRP098789       SRR5227294
    SRP098789       SRR5227295
    SRP098789       SRR5227296
    SRP098789       SRR5227297
    SRP098789       SRR5227298
    SRP098789       SRR5227299
    SRP098789       SRR5227300
    SRP098789       SRR5227301
    SRP098789       SRR5227302
    SRP098789       SRR5227303
    SRP098789       SRR5227304
    SRP098789       SRR5227305
    SRP098789       SRR5227306
    SRP098789       SRR5227307
    SRP098789       SRR5227308
    SRP098789       SRR5227309
    SRP098789       SRR5227310
    SRP098789       SRR5227311
    SRP098789       SRR5227312
    SRP098789       SRR5227313

=========================
Getting sample attributes
=========================

Often, the most useful information is in the ``sample_attribute``
column of ``SRAmetadb``. For example, what cell` types do
different experiments correspond to? What treatments have been
applied to them? This can be listed by using the ``-desc``
tag. If you also need the sample and experiment accessions,
SRS and SRX respectively, please use ``--detailed`` tag.


::

    $ pysradb srp-to-srr --desc SRP098789

    study_accession run_accession sample_attribute
    SRP098789       SRR5227288    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227289    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227290    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227291    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227292    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227293    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227294    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227295    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227296    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227297    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227298    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227299    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227300    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227301    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227302    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227303    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227304    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227305    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227306    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227307    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRR5227308    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227309    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRR5227310    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227311    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRR5227312    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227313    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq


But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srp-to-srr --detailed --desc SRP098789

    study_accession run_accession experiment_accession sample_accession study_alias experiment_alias sample_alias run_alias      sample_attribute
    SRP098789       SRR5227288    SRX2536403           SRS1956353       GSE94454    GSM2475997       GSM2475997   GSM2475997_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227289    SRX2536404           SRS1956354       GSE94454    GSM2475998       GSM2475998   GSM2475998_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227290    SRX2536405           SRS1956355       GSE94454    GSM2475999       GSM2475999   GSM2475999_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227291    SRX2536406           SRS1956356       GSE94454    GSM2476000       GSM2476000   GSM2476000_r1  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227292    SRX2536407           SRS1956357       GSE94454    GSM2476001       GSM2476001   GSM2476001_r1  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227293    SRX2536408           SRS1956358       GSE94454    GSM2476002       GSM2476002   GSM2476002_r1  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227294    SRX2536409           SRS1956359       GSE94454    GSM2476003       GSM2476003   GSM2476003_r1  source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227295    SRX2536410           SRS1956360       GSE94454    GSM2476004       GSM2476004   GSM2476004_r1  source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227296    SRX2536411           SRS1956361       GSE94454    GSM2476005       GSM2476005   GSM2476005_r1  source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRR5227297    SRX2536412           SRS1956362       GSE94454    GSM2476006       GSM2476006   GSM2476006_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227298    SRX2536413           SRS1956363       GSE94454    GSM2476007       GSM2476007   GSM2476007_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227299    SRX2536414           SRS1956364       GSE94454    GSM2476008       GSM2476008   GSM2476008_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227300    SRX2536415           SRS1956365       GSE94454    GSM2476009       GSM2476009   GSM2476009_r1  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227301    SRX2536416           SRS1956366       GSE94454    GSM2476010       GSM2476010   GSM2476010_r1  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227302    SRX2536417           SRS1956367       GSE94454    GSM2476011       GSM2476011   GSM2476011_r1  source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227303    SRX2536418           SRS1956368       GSE94454    GSM2476012       GSM2476012   GSM2476012_r1  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227304    SRX2536419           SRS1956369       GSE94454    GSM2476013       GSM2476013   GSM2476013_r1  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227305    SRX2536420           SRS1956370       GSE94454    GSM2476014       GSM2476014   GSM2476014_r1  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227306    SRX2536421           SRS1956371       GSE94454    GSM2476015       GSM2476015   GSM2476015_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227307    SRX2536422           SRS1956372       GSE94454    GSM2476016       GSM2476016   GSM2476016_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRR5227308    SRX2536423           SRS1956373       GSE94454    GSM2476017       GSM2476017   GSM2476017_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227309    SRX2536424           SRS1956374       GSE94454    GSM2476018       GSM2476018   GSM2476018_r1  source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRR5227310    SRX2536425           SRS1956375       GSE94454    GSM2476019       GSM2476019   GSM2476019_r1  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227311    SRX2536426           SRS1956376       GSE94454    GSM2476020       GSM2476020   GSM2476020_r1  source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       SRR5227312    SRX2536427           SRS1956377       GSE94454    GSM2476021       GSM2476021   GSM2476021_r1  source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       SRR5227313    SRX2536428           SRS1956378       GSE94454    GSM2476022       GSM2476022   GSM2476022_r1  source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq

==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srp-to-srr --detailed --desc --expand SRP098789

    study_accession run_accession experiment_accession sample_accession study_alias experiment_alias sample_alias run_alias      cell_line library_type source_name                                  treatment_time
    SRP098789       SRR5227288    SRX2536403           SRS1956353       GSE94454    GSM2475997       GSM2475997   GSM2475997_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRR5227289    SRX2536404           SRS1956354       GSE94454    GSM2475998       GSM2475998   GSM2475998_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRR5227290    SRX2536405           SRS1956355       GSE94454    GSM2475999       GSM2475999   GSM2475999_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRR5227291    SRX2536406           SRS1956356       GSE94454    GSM2476000       GSM2476000   GSM2476000_r1  huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRR5227292    SRX2536407           SRS1956357       GSE94454    GSM2476001       GSM2476001   GSM2476001_r1  huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRR5227293    SRX2536408           SRS1956358       GSE94454    GSM2476002       GSM2476002   GSM2476002_r1  huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       SRR5227294    SRX2536409           SRS1956359       GSE94454    GSM2476003       GSM2476003   GSM2476003_r1  huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRR5227295    SRX2536410           SRS1956360       GSE94454    GSM2476004       GSM2476004   GSM2476004_r1  huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRR5227296    SRX2536411           SRS1956361       GSE94454    GSM2476005       GSM2476005   GSM2476005_r1  huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       SRR5227297    SRX2536412           SRS1956362       GSE94454    GSM2476006       GSM2476006   GSM2476006_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227298    SRX2536413           SRS1956363       GSE94454    GSM2476007       GSM2476007   GSM2476007_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227299    SRX2536414           SRS1956364       GSE94454    GSM2476008       GSM2476008   GSM2476008_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227300    SRX2536415           SRS1956365       GSE94454    GSM2476009       GSM2476009   GSM2476009_r1  huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227301    SRX2536416           SRS1956366       GSE94454    GSM2476010       GSM2476010   GSM2476010_r1  huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227302    SRX2536417           SRS1956367       GSE94454    GSM2476011       GSM2476011   GSM2476011_r1  huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227303    SRX2536418           SRS1956368       GSE94454    GSM2476012       GSM2476012   GSM2476012_r1  huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRR5227304    SRX2536419           SRS1956369       GSE94454    GSM2476013       GSM2476013   GSM2476013_r1  huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRR5227305    SRX2536420           SRS1956370       GSE94454    GSM2476014       GSM2476014   GSM2476014_r1  huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRR5227306    SRX2536421           SRS1956371       GSE94454    GSM2476015       GSM2476015   GSM2476015_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227307    SRX2536422           SRS1956372       GSE94454    GSM2476016       GSM2476016   GSM2476016_r1  huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       SRR5227308    SRX2536423           SRS1956373       GSE94454    GSM2476017       GSM2476017   GSM2476017_r1  huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       SRR5227309    SRX2536424           SRS1956374       GSE94454    GSM2476018       GSM2476018   GSM2476018_r1  huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       SRR5227310    SRX2536425           SRS1956375       GSE94454    GSM2476019       GSM2476019   GSM2476019_r1  huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRR5227311    SRX2536426           SRS1956376       GSE94454    GSM2476020       GSM2476020   GSM2476020_r1  huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min
    SRP098789       SRR5227312    SRX2536427           SRS1956377       GSE94454    GSM2476021       GSM2476021   GSM2476021_r1  huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       SRR5227313    SRX2536428           SRS1956378       GSE94454    GSM2476022       GSM2476022   GSM2476022_r1  huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-srr --detailed --expand --saveto SRP098789_metadata.tsv SRP098789


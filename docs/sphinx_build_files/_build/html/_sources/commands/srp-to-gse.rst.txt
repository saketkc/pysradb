.. _srptogse:

##########
srp-to-gse
##########

``srp-to-gse`` converts a SRA study accession ID (SRP) to GEO accession ID (GSE).

=================
Usage and options
=================

::

    $ pysradb srp-to-gse -h
    Usage: pysradb srp-to-gse [OPTIONS] SRP_ID

      Get GSE for a SRP

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [sample_accession, run_accession]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


===========================================================
Convert SRA study accession (SRP) to GEO accession ID (GSE)
===========================================================

Gene Expression Omnibus or GEO hosts processed sequencing datasets.
The raw data is available through SRA and hence we often need to
interpolate between the two.

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding GEO experiment with ID of the form ``GSEnnnn``:

::

    $ pysradb srp-to-gse SRP098789

    study_accession study_alias
    SRP098789       GSE94454

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

    $ pysradb srp-to-gse --desc SRP098789

    study_accession study_alias sample_attribute
    SRP098789       GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       GSE94454    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq



But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srp-to-gse --detailed --desc SRP098789

    study_accession study_alias experiment_accession run_accession sample_accession experiment_alias run_alias      sample_alias sample_attribute
    SRP098789       GSE94454    SRX2536403           SRR5227288    SRS1956353       GSM2475997       GSM2475997_r1  GSM2475997   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536404           SRR5227289    SRS1956354       GSM2475998       GSM2475998_r1  GSM2475998   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536405           SRR5227290    SRS1956355       GSM2475999       GSM2475999_r1  GSM2475999   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536406           SRR5227291    SRS1956356       GSM2476000       GSM2476000_r1  GSM2476000   source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536407           SRR5227292    SRS1956357       GSM2476001       GSM2476001_r1  GSM2476001   source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536408           SRR5227293    SRS1956358       GSM2476002       GSM2476002_r1  GSM2476002   source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536409           SRR5227294    SRS1956359       GSM2476003       GSM2476003_r1  GSM2476003   source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536410           SRR5227295    SRS1956360       GSM2476004       GSM2476004_r1  GSM2476004   source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536411           SRR5227296    SRS1956361       GSM2476005       GSM2476005_r1  GSM2476005   source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536412           SRR5227297    SRS1956362       GSM2476006       GSM2476006_r1  GSM2476006   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536413           SRR5227298    SRS1956363       GSM2476007       GSM2476007_r1  GSM2476007   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536414           SRR5227299    SRS1956364       GSM2476008       GSM2476008_r1  GSM2476008   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536415           SRR5227300    SRS1956365       GSM2476009       GSM2476009_r1  GSM2476009   source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536416           SRR5227301    SRS1956366       GSM2476010       GSM2476010_r1  GSM2476010   source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536417           SRR5227302    SRS1956367       GSM2476011       GSM2476011_r1  GSM2476011   source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536418           SRR5227303    SRS1956368       GSM2476012       GSM2476012_r1  GSM2476012   source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536419           SRR5227304    SRS1956369       GSM2476013       GSM2476013_r1  GSM2476013   source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536420           SRR5227305    SRS1956370       GSM2476014       GSM2476014_r1  GSM2476014   source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536421           SRR5227306    SRS1956371       GSM2476015       GSM2476015_r1  GSM2476015   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536422           SRR5227307    SRS1956372       GSM2476016       GSM2476016_r1  GSM2476016   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       GSE94454    SRX2536423           SRR5227308    SRS1956373       GSM2476017       GSM2476017_r1  GSM2476017   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536424           SRR5227309    SRS1956374       GSM2476018       GSM2476018_r1  GSM2476018   source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       GSE94454    SRX2536425           SRR5227310    SRS1956375       GSM2476019       GSM2476019_r1  GSM2476019   source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536426           SRR5227311    SRS1956376       GSM2476020       GSM2476020_r1  GSM2476020   source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
    SRP098789       GSE94454    SRX2536427           SRR5227312    SRS1956377       GSM2476021       GSM2476021_r1  GSM2476021   source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
    SRP098789       GSE94454    SRX2536428           SRR5227313    SRS1956378       GSM2476022       GSM2476022_r1  GSM2476022   source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srp-to-gse --detailed --desc --expand SRP098789

    study_accession study_alias experiment_accession run_accession sample_accession experiment_alias run_alias      sample_alias cell_line library_type source_name                                  treatment_time
    SRP098789       GSE94454    SRX2536403           SRR5227288    SRS1956353       GSM2475997       GSM2475997_r1  GSM2475997   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       GSE94454    SRX2536404           SRR5227289    SRS1956354       GSM2475998       GSM2475998_r1  GSM2475998   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       GSE94454    SRX2536405           SRR5227290    SRS1956355       GSM2475999       GSM2475999_r1  GSM2475999   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       GSE94454    SRX2536406           SRR5227291    SRS1956356       GSM2476000       GSM2476000_r1  GSM2476000   huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       GSE94454    SRX2536407           SRR5227292    SRS1956357       GSM2476001       GSM2476001_r1  GSM2476001   huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       GSE94454    SRX2536408           SRR5227293    SRS1956358       GSM2476002       GSM2476002_r1  GSM2476002   huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRP098789       GSE94454    SRX2536409           SRR5227294    SRS1956359       GSM2476003       GSM2476003_r1  GSM2476003   huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       GSE94454    SRX2536410           SRR5227295    SRS1956360       GSM2476004       GSM2476004_r1  GSM2476004   huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       GSE94454    SRX2536411           SRR5227296    SRS1956361       GSM2476005       GSM2476005_r1  GSM2476005   huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRP098789       GSE94454    SRX2536412           SRR5227297    SRS1956362       GSM2476006       GSM2476006_r1  GSM2476006   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536413           SRR5227298    SRS1956363       GSM2476007       GSM2476007_r1  GSM2476007   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536414           SRR5227299    SRS1956364       GSM2476008       GSM2476008_r1  GSM2476008   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536415           SRR5227300    SRS1956365       GSM2476009       GSM2476009_r1  GSM2476009   huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536416           SRR5227301    SRS1956366       GSM2476010       GSM2476010_r1  GSM2476010   huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536417           SRR5227302    SRS1956367       GSM2476011       GSM2476011_r1  GSM2476011   huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536418           SRR5227303    SRS1956368       GSM2476012       GSM2476012_r1  GSM2476012   huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       GSE94454    SRX2536419           SRR5227304    SRS1956369       GSM2476013       GSM2476013_r1  GSM2476013   huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       GSE94454    SRX2536420           SRR5227305    SRS1956370       GSM2476014       GSM2476014_r1  GSM2476014   huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       GSE94454    SRX2536421           SRR5227306    SRS1956371       GSM2476015       GSM2476015_r1  GSM2476015   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536422           SRR5227307    SRS1956372       GSM2476016       GSM2476016_r1  GSM2476016   huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       GSE94454    SRX2536423           SRR5227308    SRS1956373       GSM2476017       GSM2476017_r1  GSM2476017   huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRP098789       GSE94454    SRX2536424           SRR5227309    SRS1956374       GSM2476018       GSM2476018_r1  GSM2476018   huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRP098789       GSE94454    SRX2536425           SRR5227310    SRS1956375       GSM2476019       GSM2476019_r1  GSM2476019   huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       GSE94454    SRX2536426           SRR5227311    SRS1956376       GSM2476020       GSM2476020_r1  GSM2476020   huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min
    SRP098789       GSE94454    SRX2536427           SRR5227312    SRS1956377       GSM2476021       GSM2476021_r1  GSM2476021   huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRP098789       GSE94454    SRX2536428           SRR5227313    SRS1956378       GSM2476022       GSM2476022_r1  GSM2476022   huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min

=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-gse --detailed --expand --saveto SRP098789_metadata.tsv SRP098789


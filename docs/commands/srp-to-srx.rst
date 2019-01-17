.. _srptosrx:

##########
srp-to-srx
##########

``srp-to-srx`` converts a SRA study accession (SRP) to corresponding
SRA experiment accession(s) (SRX).

=================
Usage and options
=================

::

    $ pysradb srp-to-srx -h

    Usage: pysradb srp-to-srx [OPTIONS] SRP_ID

      Get SRX/SRR for a SRP

    Options:
      --db FILE      Path to SRAmetadb.sqlite file
      --saveto TEXT  Save output to file
      --detailed     Output additional columns: [sample_accession (SRS),
                     run_accession (SRR),
                     experiment_alias (GSM),
                     sample_alias
                     (GSM_),
                     run_alias (GSM_r)',
                     study_alias (GSE)]
      --desc         Should sample_attribute be included
      --expand       Should sample_attribute be expanded
      -h, --help     Show this message and exit.


===================================================================
Convert SRA study accession (SRP) to SRA experiment accession (SRX)
===================================================================

To convert a SRA study accession of the form ``SRPmmmmm`` to its
corresponding SRA experiment accession(s) of the form ``SRXnnnn``:

::

    $ pysradb srp-to-srx SRP098789

    experiment_accession study_accession
    SRX2536403           SRP098789
    SRX2536404           SRP098789
    SRX2536405           SRP098789
    SRX2536406           SRP098789
    SRX2536407           SRP098789
    SRX2536408           SRP098789
    SRX2536409           SRP098789
    SRX2536410           SRP098789
    SRX2536411           SRP098789
    SRX2536412           SRP098789
    SRX2536413           SRP098789
    SRX2536414           SRP098789
    SRX2536415           SRP098789
    SRX2536416           SRP098789
    SRX2536417           SRP098789
    SRX2536418           SRP098789
    SRX2536419           SRP098789
    SRX2536420           SRP098789
    SRX2536421           SRP098789
    SRX2536422           SRP098789
    SRX2536423           SRP098789
    SRX2536424           SRP098789
    SRX2536425           SRP098789
    SRX2536426           SRP098789
    SRX2536427           SRP098789
    SRX2536428           SRP098789

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

    $ pysradb srp-to-srx --desc SRP098789

    experiment_accession sample_attribute                                                                                                                 study_accession
    SRX2536403           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536404           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536405           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536406           source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536407           source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536408           source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536409           source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 SRP098789
    SRX2536410           source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 SRP098789
    SRX2536411           source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 SRP098789
    SRX2536412           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536413           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536414           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536415           source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536416           source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536417           source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536418           source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536419           source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536420           source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536421           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536422           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq  SRP098789
    SRX2536423           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536424           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq  SRP098789
    SRX2536425           source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536426           source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq                 SRP098789
    SRX2536427           source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536428           source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq                 SRP098789



But without the context of individual experiment and run accessions, this information
is not so useful. In order to obtain detailed metadata:

::

    $ pysradb srp-to-srx --detailed --desc SRP098789

    experiment_accession sample_accession run_accession experiment_alias sample_alias run_alias      study_alias sample_attribute                                                                                                                 study_accession
    SRX2536403           SRS1956353       SRR5227288    GSM2475997       GSM2475997   GSM2475997_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536404           SRS1956354       SRR5227289    GSM2475998       GSM2475998   GSM2475998_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536405           SRS1956355       SRR5227290    GSM2475999       GSM2475999   GSM2475999_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536406           SRS1956356       SRR5227291    GSM2476000       GSM2476000   GSM2476000_r1  GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536407           SRS1956357       SRR5227292    GSM2476001       GSM2476001   GSM2476001_r1  GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536408           SRS1956358       SRR5227293    GSM2476002       GSM2476002   GSM2476002_r1  GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq  SRP098789
    SRX2536409           SRS1956359       SRR5227294    GSM2476003       GSM2476003   GSM2476003_r1  GSE94454    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 SRP098789
    SRX2536410           SRS1956360       SRR5227295    GSM2476004       GSM2476004   GSM2476004_r1  GSE94454    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 SRP098789
    SRX2536411           SRS1956361       SRR5227296    GSM2476005       GSM2476005   GSM2476005_r1  GSE94454    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq                 SRP098789
    SRX2536412           SRS1956362       SRR5227297    GSM2476006       GSM2476006   GSM2476006_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536413           SRS1956363       SRR5227298    GSM2476007       GSM2476007   GSM2476007_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536414           SRS1956364       SRR5227299    GSM2476008       GSM2476008   GSM2476008_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536415           SRS1956365       SRR5227300    GSM2476009       GSM2476009   GSM2476009_r1  GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536416           SRS1956366       SRR5227301    GSM2476010       GSM2476010   GSM2476010_r1  GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536417           SRS1956367       SRR5227302    GSM2476011       GSM2476011   GSM2476011_r1  GSE94454    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536418           SRS1956368       SRR5227303    GSM2476012       GSM2476012   GSM2476012_r1  GSE94454    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536419           SRS1956369       SRR5227304    GSM2476013       GSM2476013   GSM2476013_r1  GSE94454    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536420           SRS1956370       SRR5227305    GSM2476014       GSM2476014   GSM2476014_r1  GSE94454    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536421           SRS1956371       SRR5227306    GSM2476015       GSM2476015   GSM2476015_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536422           SRS1956372       SRR5227307    GSM2476016       GSM2476016   GSM2476016_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq  SRP098789
    SRX2536423           SRS1956373       SRR5227308    GSM2476017       GSM2476017   GSM2476017_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq  SRP098789
    SRX2536424           SRS1956374       SRR5227309    GSM2476018       GSM2476018   GSM2476018_r1  GSE94454    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq  SRP098789
    SRX2536425           SRS1956375       SRR5227310    GSM2476019       GSM2476019   GSM2476019_r1  GSE94454    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536426           SRS1956376       SRR5227311    GSM2476020       GSM2476020   GSM2476020_r1  GSE94454    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq                 SRP098789
    SRX2536427           SRS1956377       SRR5227312    GSM2476021       GSM2476021   GSM2476021_r1  GSE94454    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq                 SRP098789
    SRX2536428           SRS1956378       SRR5227313    GSM2476022       GSM2476022   GSM2476022_r1  GSE94454    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq                 SRP098789


==============================================================
Expanding the ``sample_attribute`` column to one per attribute
==============================================================

The data in ``sample_attribute`` does not have a
predefined structure and hence in order to make it
more parsable we split it into multiple columns
using the ``--expand`` flag.

::

    $ pysradb srp-to-srx --detailed --desc --expand SRP098789

    experiment_accession sample_accession run_accession experiment_alias sample_alias run_alias      study_alias study_accession cell_line library_type source_name                                  treatment_time
    SRX2536403           SRS1956353       SRR5227288    GSM2475997       GSM2475997   GSM2475997_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRX2536404           SRS1956354       SRR5227289    GSM2475998       GSM2475998   GSM2475998_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRX2536405           SRS1956355       SRR5227290    GSM2475999       GSM2475999   GSM2475999_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRX2536406           SRS1956356       SRR5227291    GSM2476000       GSM2476000   GSM2476000_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRX2536407           SRS1956357       SRR5227292    GSM2476001       GSM2476001   GSM2476001_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRX2536408           SRS1956358       SRR5227293    GSM2476002       GSM2476002   GSM2476002_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
    SRX2536409           SRS1956359       SRR5227294    GSM2476003       GSM2476003   GSM2476003_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRX2536410           SRS1956360       SRR5227295    GSM2476004       GSM2476004   GSM2476004_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRX2536411           SRS1956361       SRR5227296    GSM2476005       GSM2476005   GSM2476005_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_10 min_ribo-seq                 10 min
    SRX2536412           SRS1956362       SRR5227297    GSM2476006       GSM2476006   GSM2476006_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536413           SRS1956363       SRR5227298    GSM2476007       GSM2476007   GSM2476007_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536414           SRS1956364       SRR5227299    GSM2476008       GSM2476008   GSM2476008_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536415           SRS1956365       SRR5227300    GSM2476009       GSM2476009   GSM2476009_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536416           SRS1956366       SRR5227301    GSM2476010       GSM2476010   GSM2476010_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536417           SRS1956367       SRR5227302    GSM2476011       GSM2476011   GSM2476011_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536418           SRS1956368       SRR5227303    GSM2476012       GSM2476012   GSM2476012_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRX2536419           SRS1956369       SRR5227304    GSM2476013       GSM2476013   GSM2476013_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRX2536420           SRS1956370       SRR5227305    GSM2476014       GSM2476014   GSM2476014_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRX2536421           SRS1956371       SRR5227306    GSM2476015       GSM2476015   GSM2476015_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536422           SRS1956372       SRR5227307    GSM2476016       GSM2476016   GSM2476016_r1  GSE94454    SRP098789       huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRX2536423           SRS1956373       SRR5227308    GSM2476017       GSM2476017   GSM2476017_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_60 min_ribo-seq  60 min
    SRX2536424           SRS1956374       SRR5227309    GSM2476018       GSM2476018   GSM2476018_r1  GSE94454    SRP098789       huh7      polya-seq    huh7_1.5 ã‚âµm pf-067446846_60 min_rna-seq   60 min
    SRX2536425           SRS1956375       SRR5227310    GSM2476019       GSM2476019   GSM2476019_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRX2536426           SRS1956376       SRR5227311    GSM2476020       GSM2476020   GSM2476020_r1  GSE94454    SRP098789       huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min
    SRX2536427           SRS1956377       SRR5227312    GSM2476021       GSM2476021   GSM2476021_r1  GSE94454    SRP098789       huh7      ribo-seq     huh7_vehicle_60 min_ribo-seq                 60 min
    SRX2536428           SRS1956378       SRR5227313    GSM2476022       GSM2476022   GSM2476022_r1  GSE94454    SRP098789       huh7      polya-seq    huh7_vehicle_60 min_rna-seq                  60 min


=========================
Saving metadata to a file
=========================

``pysradb`` follows a consistent pattern for providing
an option to save output of any of its subcommands to a file
using the ``--saveto`` argument:

::

    $ pysradb srp-to-srx --detailed --expand --saveto SRP098789_metadata.tsv SRP098789

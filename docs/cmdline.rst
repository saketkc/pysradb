.. _clitutorial:

############
CLI Tutorial
############

::

   $ pysradb
    Usage: pysradb [OPTIONS] COMMAND [ARGS]...

      pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.

      Citation: Pending.

    Options:
      --version   Show the version and exit.
      -h, --help  Show this message and exit.

    Commands:
      download    Download SRA project (SRPnnnn)
      gse-to-gsm  Get GSM for a GSE
      gse-to-srp  Get SRP for a GSE
      gsm-to-gse  Get GSE for a GSM
      gsm-to-srp  Get SRP for a GSM
      gsm-to-srr  Get SRR for a GSM
      gsm-to-srx  Get SRX for a GSM
      metadata    Fetch metadata for SRA project (SRPnnnn)
      metadb      Download SRAmetadb.sqlite
      search      Search SRA for matching text
      srp-to-gse  Get GSE for a SRP
      srp-to-srr  Get SRR for a SRP
      srp-to-srs  Get SRS for a SRP
      srp-to-srx  Get SRX for a SRP
      srr-to-srp  Get SRP for a SRR
      srr-to-srs  Get SRS for a SRR
      srr-to-srx  Get SRX for a SRR
      srs-to-srx  Get SRX for a SRS
      srx-to-srp  Get SRP for a SRX
      srx-to-srr  Get SRR for a SRX
      srx-to-srs  Get SRS for a SRX


All the operations in `pysradb` rely on the SQLite file `SRAmetadb.sqlite` provided
by the SRAdb project. We can download it using `pysradb`:

::

   $ pysradb srametadb

This will download and extract ``SRAmetadb.sqlite.gz`` in the current directory.
you can also specify an output directory using ``--out-dir`` option.


::

   $ pysradb srametadb -h

    Usage: pysradb srametadb [OPTIONS]

      Download SRAmetadb.sqlite

    Options:
      --out-dir TEXT       Output directory location
      --overwrite BOOLEAN  Overwrite existing file
      -h, --help           Show this message and exit.



Having obtained the SQLite file, we can now perform all our data/metadata seach
operations. For the rest of this walkthrough we will assume the
sqlite directory exists in the current working directory, so that
we do not need to specify the path to `pysradb`.


========================================
Getting metadata for a SRA project (SRP)
========================================

The most basic information associated with any SRA project is its list of experiments
and run accessions.


::

   $ pysradb metadata SRP098789

    study_accession experiment_accession sample_accession run_accession
    SRP098789       SRX2536403           SRS1956353       SRR5227288
    SRP098789       SRX2536404           SRS1956354       SRR5227289
    SRP098789       SRX2536405           SRS1956355       SRR5227290
    SRP098789       SRX2536406           SRS1956356       SRR5227291
    SRP098789       SRX2536407           SRS1956357       SRR5227292
    SRP098789       SRX2536408           SRS1956358       SRR5227293
    SRP098789       SRX2536409           SRS1956359       SRR5227294



Listing SRX and SRRs for a SRP is often not useful. We might
want to take a quick look at the metadata associated with
the samples:

::

   $ pysradb metadata SRP098789 --desc

    study_accession experiment_accession sample_accession run_accession sample_attribute
    SRP098789       SRX2536403           SRS1956353       SRR5227288    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536404           SRS1956354       SRR5227289    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536405           SRS1956355       SRR5227290    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536406           SRS1956356       SRR5227291    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536407           SRS1956357       SRR5227292    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536408           SRS1956358       SRR5227293    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


Better still, we might need to separate out the information in `source_name` column to multiple
columns. For example, in the above example, we might need the `cell line` information in
a separate column. This is achieved by `--expand` flag:

::

   $ pysradb metadata SRP098789 --desc --expand

   study_accession experiment_accession sample_accession run_accession cell_line library_type source_name                                  treatment_time
   SRP098789       SRX2536403           SRS1956353       SRR5227288    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
   SRP098789       SRX2536404           SRS1956354       SRR5227289    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
   SRP098789       SRX2536405           SRS1956355       SRR5227290    huh7      ribo-seq     huh7_1.5 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
   SRP098789       SRX2536406           SRS1956356       SRR5227291    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min
   SRP098789       SRX2536407           SRS1956357       SRR5227292    huh7      ribo-seq     huh7_0.3 ã‚âµm pf-067446846_10 min_ribo-seq  10 min


The example here came from a Ribosome profiling study and consists of a collection of
both Ribo-seq and RNA-seq samples. In order to filter out only the RNA-seq samples,
we could pass it an extra flag of `--assay` and then filter RNA-seq samples.

::

   $ pysradb metadata SRP098789 --assay | grep 'study|RNA-Seq'

   SRP098789       SRX2536422           SRR5227307    RNA-Seq          SINGLE -
   SRP098789       SRX2536424           SRR5227309    RNA-Seq          SINGLE -
   SRP098789       SRX2536426           SRR5227311    RNA-Seq          SINGLE -
   SRP098789       SRX2536428           SRR5227313    RNA-Seq          SINGLE -

A more complicated example will consist of multiple assays. For example `SRP000941`:

::

   $ pysradb metadata --db data/SRAmetadb.sqlite SRP000941 --assay  | tr -s '  ' | cut -f5 -d ' ' | sort | uniq -c
   999 Bisulfite-Seq
   768 ChIP-Seq
     1 library_strategy
   121 OTHER
   353 RNA-Seq
    28 WGS


====================================================
Get experiment accessions for a project (SRP => SRX)
====================================================

A frequently encountered task involves getting all the
experiments (SRX) for a particular study accession (SRP).
Consider project `SRP048759`:

::

   $ pysradb srp-to-srx SRP048759

================================================
Get sample accessions for a project (SRP => SRS)
================================================

Each experiment involves one or multiple biological samples (SRS),
that are put through different experiments (SRX).

::

   $ pysradb srp-to-srs --detailed SRP048759

   study_accession sample_accession
   SRP048759       SRS718878
   SRP048759       SRS718879
   SRP048759       SRS718880
   SRP048759       SRS718881
   SRP048759       SRS718882
   SRP048759       SRS718883
   SRP048759       SRS718884
   SRP048759       SRS718885
   SRP048759       SRS718886

This is very limited information. It can again be detailed out
using the `--detailed` flag:

::

   $ pysradb srp-to-srs --detailed SRP048759

   study_accession sample_accession        experiment_accession    run_accession   study_alias     sample_alias    experiment_alias        run_alias
   SRP048759       SRS718878       SRX729552       SRR1608490      GSE62190        GSM1521543      GSM1521543      GSM1521543_r1
   SRP048759       SRS718878       SRX729552       SRR1608491      GSE62190        GSM1521543      GSM1521543      GSM1521543_r2
   SRP048759       SRS718878       SRX729552       SRR1608492      GSE62190        GSM1521543      GSM1521543      GSM1521543_r3
   SRP048759       SRS718878       SRX729552       SRR1608493      GSE62190        GSM1521543      GSM1521543      GSM1521543_r4
   SRP048759       SRS718879       SRX729553       SRR1608494      GSE62190        GSM1521544      GSM1521544      GSM1521544_r1
   SRP048759       SRS718879       SRX729553       SRR1608495      GSE62190        GSM1521544      GSM1521544      GSM1521544_r2



===============================================
Get run accessions for experiments (SRX => SRR)
===============================================

Another frequently encountered task involves fetching the run accessions (SRR)
for a particular experiment (SRX). Consider experiments `SRX217956` and
`SRX2536403`. We want to be able to resolve the run accessions for these
experiments:

::

   $ pysradb srx-to-srr SRX217956  SRX2536403 --desc

   experiment_accession run_accession study_accession sample_attribute
   SRX217956            SRR649752     SRP017942       source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRX2536403           SRR5227288    SRP098789       source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


===============================================
Get experiment accessions for runs (SRR => SRX)
===============================================

For fetching experiment accessions (SRX) for one or multiple
run accessions (SRR):

::

   $ pysradb srr-to-srx --db data/SRAmetadb.sqlite SRR5227288 SRR649752 --desc
   run_accession study_accession experiment_accession sample_attribute
   SRR649752     SRP017942       SRX217956            source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRR5227288    SRP098789       SRX2536403           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq



::

   $ pysradb metadata --db data/SRAmetadb.sqlite --assay SRP098789 | pysradb download --db data/SRAmetadb.sqlite


===========================================
Get GEO accessions for studies (SRP => GSE)
===========================================

**SRP to GSE:**

::

   $ pysradb srp-to-gse SRP090415

   study_accession study_alias
   SRP090415       GSE87328

**But not all SRPs will have an associated GEO id (GSE):**

::

   $ pysradb srp-to-gse SRP029589

   study_accession study_alias
   SRP029589       PRJNA218051


===============================================
Get SRA accessions for GEO studies (GSE => SRP)
===============================================

::

    $ pysradb gse-to-srp GSE87328i

    study_alias study_accession
    GSE87328    SRP090415

=============
Searching SRA
=============

::

    $ pysradb search 'cycloheximide heatshock'

    study_accession experiment_accession sample_accession run_accession
    SRP044649       SRX657376            SRS662567        SRR1520327
    SRP044649       SRX657377            SRS662568        SRR1520328


Please see `quickstart <https://www.saket-choudhary.me/pysradb/quickstart.html#the-full-list-of-possible-pysradb-operations>`_ for all possible operations available through ``pysradb``.

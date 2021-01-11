.. _clitutorial:

####
CLI
####

::

    $ pysradb
    usage: pysradb [-h] [--version] [--citation]
                   {metadb,metadata,download,search,gse-to-gsm,gse-to-srp,gsm-to-gse,gsm-to-srp,gsm-to-srr,gsm-to-srs,gsm-to-srx,srp-to-gse,srp-to-srr,srp-to-srs,srp-to-srx,srr-to-gsm,srr-to-srp,srr-to-srs,srr-to-srx,srs-to-gsm,srs-to-srx,srx-to-srp,srx-to-srr,srx-to-srs}
                   ...

    pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.
    Citation: 10.12688/f1000research.18676.1

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --citation            how to cite

    subcommands:
      {metadb,metadata,download,search,gse-to-gsm,gse-to-srp,gsm-to-gse,gsm-to-srp,gsm-to-srr,gsm-to-srs,gsm-to-srx,srp-to-gse,srp-to-srr,srp-to-srs,srp-to-srx,srr-to-gsm,srr-to-srp,srr-to-srs,srr-to-srx,srs-to-gsm,srs-to-srx,srx-to-srp,srx-to-srr,srx-to-srs}
        metadata            Fetch metadata for SRA project (SRPnnnn)
        download            Download SRA project (SRPnnnn)
        search              Search SRA/ENA for matching text
        gse-to-gsm          Get GSM for a GSE
        gse-to-srp          Get SRP for a GSE
        gsm-to-gse          Get GSE for a GSM
        gsm-to-srp          Get SRP for a GSM
        gsm-to-srr          Get SRR for a GSM
        gsm-to-srs          Get SRS for a GSM
        gsm-to-srx          Get SRX for a GSM
        srp-to-gse          Get GSE for a SRP
        srp-to-srr          Get SRR for a SRP
        srp-to-srs          Get SRS for a SRP
        srp-to-srx          Get SRX for a SRP
        srr-to-gsm          Get GSM for a SRR
        srr-to-srp          Get SRP for a SRR
        srr-to-srs          Get SRS for a SRR
        srr-to-srx          Get SRX for a SRR
        srs-to-gsm          Get GSM for a SRS
        srs-to-srx          Get SRX for a SRS
        srx-to-srp          Get SRP for a SRX
        srx-to-srr          Get SRR for a SRX
        srx-to-srs          Get SRS for a SRX


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

   $ pysradb metadata SRP098789

    study_accession experiment_accession sample_accession run_accession sample_attribute
    SRP098789       SRX2536403           SRS1956353       SRR5227288    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536404           SRS1956354       SRR5227289    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536405           SRS1956355       SRR5227290    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536406           SRS1956356       SRR5227291    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536407           SRS1956357       SRR5227292    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536408           SRS1956358       SRR5227293    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


The example here came from a Ribosome profiling study and consists of a collection of
both Ribo-seq and RNA-seq samples. We can filter out only the RNA-seq samples:

::

   $ pysradb metadata SRP098789 --detailed | grep 'study|RNA-Seq'

   SRP098789       SRX2536422           SRR5227307    RNA-Seq          SINGLE -
   SRP098789       SRX2536424           SRR5227309    RNA-Seq          SINGLE -
   SRP098789       SRX2536426           SRR5227311    RNA-Seq          SINGLE -
   SRP098789       SRX2536428           SRR5227313    RNA-Seq          SINGLE -

A more complicated example will consist of multiple assays. For example `SRP000941`:

::

   $ pysradb metadata SRP000941 --detailed  | tr -s '  ' | cut -f5 -d ' ' | sort | uniq -c
   999 Bisulfite-Seq
   768 ChIP-Seq
     1 library_strategy
   121 OTHER
   353 RNA-Seq
    28 WGS


====================================================
Experiment accessions for a project (SRP => SRX)
====================================================

A frequently encountered task involves getting all the
experiments (SRX) for a particular study accession (SRP).
Consider project `SRP048759`:

::

   $ pysradb srp-to-srx SRP048759

================================================
Sample accessions for a project (SRP => SRS)
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
Run accessions for experiments (SRX => SRR)
===============================================

Another frequently encountered task involves fetching the run accessions (SRR)
for a particular experiment (SRX). Consider experiments `SRX217956` and
`SRX2536403`. We want to be able to resolve the run accessions for these
experiments:

::

   $ pysradb srx-to-srr SRX217956  SRX2536403 --detailed

   experiment_accession run_accession study_accession sample_attribute
   SRX217956            SRR649752     SRP017942       source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRX2536403           SRR5227288    SRP098789       source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


===============================================
Experiment accessions for runs (SRR => SRX)
===============================================

For fetching experiment accessions (SRX) for one or multiple
run accessions (SRR):

::

   $ pysradb srr-to-srx SRR5227288 SRR649752 --detailed
   run_accession study_accession experiment_accession sample_attribute
   SRR649752     SRP017942       SRX217956            source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRR5227288    SRP098789       SRX2536403           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq



===========================
Downaloading entire project
===========================

::

   $ pysradb metadata --detailed SRP098789 | pysradb download


===========================================
GEO accessions for studies (SRP => GSE)
===========================================


::

   $ pysradb srp-to-gse SRP090415

   study_accession study_alias
   SRP090415       GSE87328

But not all SRPs will have an associated GEO id (GSE):

::

   $ pysradb srp-to-gse SRP029589

   study_accession study_alias
   SRP029589       PRJNA218051


===============================================
SRA accessions for GEO studies (GSE => SRP)
===============================================

::

    $ pysradb gse-to-srp GSE87328i

    study_alias study_accession
    GSE87328    SRP090415


Please see `quickstart <https://www.saket-choudhary.me/pysradb/quickstart.html#the-full-list-of-possible-pysradb-operations>`_ for all possible operations available through ``pysradb``.

#########
CLI usage
#########

All the operations in `pysradb` rely on the SQLite file `SRAmetadb.sqlite` provided
by the SRAdb project. We can download it using `pysradb`:

.. code-block:: bash

   $ pysradb srametadb

This will download and extract `SRAmetadb.sqlite.gz` in the current directory.
you can also specify an output directory using `--out_dir` option.


.. code-block:: bash

  $ pysradb srametadb -h

    Usage: pysradb srametadb [OPTIONS]

      Download SRAmetadb.sqlite

    Options:
      --out_dir TEXT       Output directory location
      --overwrite BOOLEAN  Overwrite existing file
      -h, --help           Show this message and exit.



Having obtained the SQLite file, we can now perform all our data/metadata seach
operations. For the rest of this walkthrough we will assume the
sqlite directory exists in the current working directory, so that
we do not need to specify the path to `pysradb`.


Gettng metadata for a SRA project (SRP)
=======================================

The most basic information associated with any SRA project is its list of experiments
and run accessions.


.. code-block:: bash

   $ pysradb sra-metadata SRP098789
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

.. code-block:: bash

   $  pysradb sra-metadata SRP098789 --desc

    study_accession experiment_accession sample_accession run_accession sample_attribute
    SRP098789       SRX2536403           SRS1956353       SRR5227288    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536404           SRS1956354       SRR5227289    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536405           SRS1956355       SRR5227290    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536406           SRS1956356       SRR5227291    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536407           SRS1956357       SRR5227292    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
    SRP098789       SRX2536408           SRS1956358       SRR5227293    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq

The example here came from a Ribosome profiling study and consists of a collection of
both Ribo-seq and RNA-seq samples. In order to filter out only the RNA-seq samples,
we could pass it an extra flag of `--assay` and then filter RNA-seq samples.

.. code-block:: bash

   $ pysradb sra-metadata SRP098789 --assay | grep 'study|RNA-Seq'
   SRP098789       SRX2536422           SRR5227307    RNA-Seq          SINGLE -
   SRP098789       SRX2536424           SRR5227309    RNA-Seq          SINGLE -
   SRP098789       SRX2536426           SRR5227311    RNA-Seq          SINGLE -
   SRP098789       SRX2536428           SRR5227313    RNA-Seq          SINGLE -

A more complicated example will consist of multiple assays. For example `SRP000941`:

.. code-block:: bash

   $ pysradb sra-metadata --db data/SRAmetadb.sqlite SRP000941 --assay  | tr -s '  ' | cut -f4 -d ' ' | sort | uniq -c
   999 Bisulfite-Seq
   768 ChIP-Seq
     1 library_strategy
   121 OTHER
   353 RNA-Seq
    28 WGS


Get experiment accesions for a project (SRP => SRX)
===================================================

A frequently encountered task involves getting all the
experiments (SRX) for a particular study accession (SRP).
Consider project `SRP048759`:

.. code-block:: bash

   $ pysradb srp-to-srx SRP048759

Get sample accesions for a project (SRP => SRS)



Get run accessions for experiments (SRX => SRR)
===============================================

Another frequently encountered task involves fetching the run accessions (SRR)
for a particular experiment (SRX). Consider experiments `SRX217956` and
`SRX2536403`. We want to be able to resolve the run accessions for these
experiments:

.. code-block:: bash

   $ pysradb srx-to-srr SRX217956  SRX2536403 --desc
   experiment_accession run_accession study_accession sample_attribute
   SRX217956            SRR649752     SRP017942       source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRX2536403           SRR5227288    SRP098789       source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


Get experiment accessions for runs (SRR => SRX)
===============================================

For fetching experiment accessions (SRX) for one or multiple
run accessions (SRR):

.. code-block:: bash

   $ pysradb srr-to-srx --db data/SRAmetadb.sqlite SRR5227288 SRR649752 --desc
   run_accession study_accession experiment_accession sample_attribute
   SRR649752     SRP017942       SRX217956            source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRR5227288    SRP098789       SRX2536403           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq



.. code-block:: bash

   $ pysradb sra-metadata --db data/SRAmetadb.sqlite --assay SRP098789 | pysradb download --db data/SRAmetadb.sqlite


Conversions
-----------

SRP to GSE:

.. code-block:: bash

   $ pysradb srp-to-gse SRP090415
   study_accession study_alias
   SRP090415       GSE87328

But not all SRPs will have an associated GEO id (GSE):

.. code-block:: bash

   $ pysradb srp-to-gse SRP029589
   study_accession study_alias
   SRP029589       PRJNA218051


GSE to SRP:

.. code-block:: bash

    $ pysradb gse-to-srp GSE87328
    study_alias study_accession
    GSE87328    SRP090415



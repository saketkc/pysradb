#########
CLI usage
#########

Getting metadata for a SRP id:


.. code-block:: bash

   $ pysradb sra-metadata --db data/SRAmetadb.sqlite SRP098789
   study_accession experiment_accession run_accession
   SRP098789       SRX2536403           SRR5227288
   SRP098789       SRX2536404           SRR5227289
   SRP098789       SRX2536405           SRR5227290
   SRP098789       SRX2536406           SRR5227291
   SRP098789       SRX2536407           SRR5227292
   SRP098789       SRX2536408           SRR5227293
   SRP098789       SRX2536409           SRR5227294
   SRP098789       SRX2536410           SRR5227295
   SRP098789       SRX2536411           SRR5227296
   SRP098789       SRX2536412           SRR5227297
   SRP098789       SRX2536413           SRR5227298
   SRP098789       SRX2536414           SRR5227299
   SRP098789       SRX2536415           SRR5227300
   SRP098789       SRX2536416           SRR5227301
   SRP098789       SRX2536417           SRR5227302
   SRP098789       SRX2536418           SRR5227303
   SRP098789       SRX2536419           SRR5227304
   SRP098789       SRX2536420           SRR5227305
   SRP098789       SRX2536421           SRR5227306
   SRP098789       SRX2536422           SRR5227307
   SRP098789       SRX2536423           SRR5227308
   SRP098789       SRX2536424           SRR5227309
   SRP098789       SRX2536425           SRR5227310
   SRP098789       SRX2536426           SRR5227311
   SRP098789       SRX2536427           SRR5227312
   SRP098789       SRX2536428           SRR5227313


Listing SRX and SRRs for a SRP is often not useful. We might
want to take a quick look at the metadata associated with
the samples:

.. code-block:: bash

   $  pysradb sra-metadata --db data/SRAmetadb.sqlite SRP098789 --desc
   study_accession experiment_accession run_accession sample_attribute
   SRP098789       SRX2536403           SRR5227288    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536404           SRR5227289    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536405           SRR5227290    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536406           SRR5227291    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536407           SRR5227292    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536408           SRR5227293    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536409           SRR5227294    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536410           SRR5227295    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536411           SRR5227296    source_name: Huh7_vehicle_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq
   SRP098789       SRX2536412           SRR5227297    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536413           SRR5227298    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536414           SRR5227299    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536415           SRR5227300    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536416           SRR5227301    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536417           SRR5227302    source_name: Huh7_0.3 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536418           SRR5227303    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536419           SRR5227304    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536420           SRR5227305    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536421           SRR5227306    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536422           SRR5227307    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
   SRP098789       SRX2536423           SRR5227308    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536424           SRR5227309    source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
   SRP098789       SRX2536425           SRR5227310    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536426           SRR5227311    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq
   SRP098789       SRX2536427           SRR5227312    source_name: Huh7_vehicle_60 min_ribo-seq || cell line: Huh7 || treatment time: 60 min || library type: ribo-seq
   SRP098789       SRX2536428           SRR5227313    source_name: Huh7_vehicle_60 min_RNA-seq || cell line: Huh7 || treatment time: 60 min || library type: polyA-seq


The example here came from a Ribosome profiling study and consists of a collection of
both Ribo-seq and RNA-seq samples. In order to filter out only the RNA-seq samples,
we could pass it an extra flag of `--assay` and then filter RNA-seq samples.

.. code-block:: bash

   $ pysradb sra-metadata --db data/SRAmetadb.sqlite SRP098789 --assay | grep RNA-Seq
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


Getting SRR for SRX:

.. code-block:: bash

   $ pysradb srx-to-srr --db data/SRAmetadb.sqlite SRX217956  SRX2536403 --desc
   experiment_accession run_accession study_accession sample_attribute
   SRX217956            SRR649752     SRP017942       source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRX2536403           SRR5227288    SRP098789       source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


Get SRX for SRR:

.. code-block:: bash

   $ pysradb srr-to-srx --db data/SRAmetadb.sqlite SRR5227288 SRR649752 --desc
   run_accession study_accession experiment_accession sample_attribute
   SRR649752     SRP017942       SRX217956            source_name: 3T3 cells || treatment: control || cell line: 3T3 cells || assay type: Riboseq
   SRR5227288    SRP098789       SRX2536403           source_name: Huh7_1.5 Ã‚ÂµM PF-067446846_10 min_ribo-seq || cell line: Huh7 || treatment time: 10 min || library type: ribo-seq


Piped downloads:

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



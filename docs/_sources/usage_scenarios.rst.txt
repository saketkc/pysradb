.. _usagescenarios:

###############
Usage Scenarios
###############


==========
Scenario 1
==========

Consider a scenario where somone is interested in searching for single-cell
RNA-seq datasets. In particular, the interest is in studying retina:


::

   $ pysradb search '"single-cell rna-seq" retina' | head

    study_accession experiment_accession sample_accession run_accession
    SRP073242       SRX1702108           SRS1397509       SRR3375520
    SRP073242       SRX1702109           SRS1397507       SRR3375521
    SRP073242       SRX1702110           SRS1397508       SRR3375522
    SRP073242       SRX1702111           SRS1397505       SRR3375523
    SRP073242       SRX1702112           SRS1397506       SRR3375524
    SRP073242       SRX1702113           SRS1397504       SRR3375525
    SRP073242       SRX1702114           SRS1397503       SRR3375526
    SRP073242       SRX1702115           SRS1397502       SRR3375527
    SRP073242       SRX1702116           SRS1397500       SRR3375528

``SRP073242`` seems like a project of interest. However the information
outputted by the ``search`` command is pretty limited. We want to
look up more detailed information about this project:

::

   $ pysradb metadata SRP075720 --desc --expand | head

    study_accession experiment_accession sample_accession run_accession developmental_stage retina_id source_name                tissue
    SRP075720       SRX1800089           SRS1467259       SRR3587529    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800090           SRS1467260       SRR3587530    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800091           SRS1467261       SRR3587531    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800092           SRS1467262       SRR3587532    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800093           SRS1467263       SRR3587533    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800094           SRS1467264       SRR3587534    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800095           SRS1467265       SRR3587535    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800096           SRS1467266       SRR3587536    p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800097           SRS1467267       SRR3587537    p17                 1ra       mus musculus retina__ p17  retina


The ``--desc`` flag feteches the description while ``--expand`` organizes this description into separate columns.
This is often useful in cases where you want to determine the treatment condition or tissue type or any other relevant
condition of the experiment.
It is also possible to get more detailed information using the ``--detailed`` flag:


::

   $ pysradb metadata SRP075720 --detailed --expand | head

    study_accession experiment_accession sample_accession run_accession experiment_title                                  experiment_attribute        taxon_id library_selection library_layout library_strategy library_source  library_name  bases      spots   adapter_spec  avg_read_length developmental_stage retina_id source_name                tissue
    SRP075720       SRX1800089           SRS1467259       SRR3587529    GSM2177186: Kcng4_1Ra_A10; Mus musculus; RNA-Seq  GEO Accession: GSM2177186  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         79101650   1582033  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800090           SRS1467260       SRR3587530    GSM2177187: Kcng4_1Ra_A11; Mus musculus; RNA-Seq  GEO Accession: GSM2177187  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         84573650   1691473  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800091           SRS1467261       SRR3587531    GSM2177188: Kcng4_1Ra_A12; Mus musculus; RNA-Seq  GEO Accession: GSM2177188  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         77835550   1556711  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800092           SRS1467262       SRR3587532    GSM2177189: Kcng4_1Ra_A1; Mus musculus; RNA-Seq   GEO Accession: GSM2177189  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         73905150   1478103  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800093           SRS1467263       SRR3587533    GSM2177190: Kcng4_1Ra_A2; Mus musculus; RNA-Seq   GEO Accession: GSM2177190  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         77193150   1543863  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800094           SRS1467264       SRR3587534    GSM2177191: Kcng4_1Ra_A3; Mus musculus; RNA-Seq   GEO Accession: GSM2177191  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         59205550   1184111  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800095           SRS1467265       SRR3587535    GSM2177192: Kcng4_1Ra_A4; Mus musculus; RNA-Seq   GEO Accession: GSM2177192  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         61794700   1235894  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800096           SRS1467266       SRR3587536    GSM2177193: Kcng4_1Ra_A5; Mus musculus; RNA-Seq   GEO Accession: GSM2177193  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         78437650   1568753  None         50.0             p17                 1ra       mus musculus retina__ p17  retina
    SRP075720       SRX1800097           SRS1467267       SRR3587537    GSM2177194: Kcng4_1Ra_A6; Mus musculus; RNA-Seq   GEO Accession: GSM2177194  10090     cDNA              SINGLE -       RNA-Seq          TRANSCRIPTOMIC  None         77392700   1547854  None         50.0             p17                 1ra       mus musculus retina__ p17  retina


Having made sure this dataset is indeed of interest, we want to save some work and see
if the processed dataset has been made available on GEO by the authors:

::

    $ pysradb srp-to-gse SRP075720

    study_accession study_alias
    SRP075720       GSE81903

So indeed a GEO project exists fot this SRA dataset.


Notice, that the GEO information was also visible in the ``metadata --detailed`` operation.
Assume we were in posession of the GSM id of one of the experiments to start off with, say
``GSM2177186``. Starting from this GSM id, we want to get the following information:

* SRP id of the project
* GSE id of the project
* SRX id of the experiment
* SRR id(s) corresponding to the experiment


Get SRP id:


::

    $ pysradb gsm-to-srp GSM2177186

    experiment_alias study_accession
    GSM2177186       SRP075720


Get GSE id:

::

    $ pysradb gsm-to-gse GSM2177186

    experiment_alias study_alias
    GSM2177186       GSE81903

Get SRX id:

::

    $ pysradb gsm-to-srx GSM2177186

    experiment_alias experiment_accession
    GSM2177186       SRX1800089

Getting SRR id(s):

::

    $ pysradb gsm-to-srr GSM2177186

    experiment_alias run_accession
    GSM2177186       SRR3587529


At any of the steps , we could have used the ``--detailed``, ``--desc`` and ``--expand`` flags to get entire metadata.
For example:

::

    $ pysradb gsm-to-srr GSM2177186 --detailed --desc --expand

    experiment_alias run_accession experiment_accession sample_accession study_accession run_alias      sample_alias study_alias developmental_stage retina_id source_name                tissue
    GSM2177186       SRR3587529    SRX1800089           SRS1467259       SRP075720       GSM2177186_r1  GSM2177186   GSE81903    p17                 1ra       mus musculus retina__ p17  retina

==========
Scenario 2
==========

Our first scenario included metadata search. In this second scenario,
we explore downloading datasets.

We have a SRP id to start off with: ``SRP000941``. We want to
quickly checkout its contents:

::

    $ pysradb metadata SRP000941 --assay --desc --expand | head

    study_accession experiment_accession sample_accession run_accession library_strategy batch         biomaterial_provider             biomaterial_type cell_type    collection_method differentiation_method                                                                                                                     differentiation_stage                                                                disease                                                          donor_age donor_ethnicity                 donor_health_status                                                                                 donor_id donor_sex line          lineage                                                               medium                                                                                                                                                                                                   molecule     passage                             sample_term_id  sex     source_name              tissue                   tissue_depot tissue_type
    SRP000941       SRX006235            SRS004118        SRR018454     ChIP-Seq         NaN           cellular dynamics international  cell line        NaN          NaN               none                                                                                                                                       none                                                                                 none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            embryonic stem cell                                                   mteser                                                                                                                                                                                                   genomic dna  between 30 and 50                   efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006236            SRS004118        SRR018456     ChIP-Seq         NaN           cellular dynamics international  cell line        NaN          NaN               none                                                                                                                                       none                                                                                 none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            embryonic stem cell                                                   mteser                                                                                                                                                                                                   genomic dna  between 30 and 50                   efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006237            SRS004118        SRR018455     ChIP-Seq         NaN           cellular dynamics international  cell line        NaN          NaN               none                                                                                                                                       none                                                                                 none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            embryonic stem cell                                                   mteser                                                                                                                                                                                                   genomic dna  between 30 and 50                   efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019072     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019080     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019081     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019082     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019083     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN
    SRP000941       SRX006239            SRS004213        SRR019084     Bisulfite-Seq    #2            thomson laboratory               cell line        NaN          NaN               na                                                                                                                                         embryonic stem cell                                                                  none                                                             NaN       NaN                             NaN                                                                                                 NaN      NaN       h1            na                                                                    tesr                                                                                                                                                                                                     genomic dna  27                                  efo_0003042     male    NaN                      NaN                      NaN          NaN


This project is a collection of multiple assays.

::

    $ pysradb metadata SRP000941 --assay  | tr -s '  ' | cut -f5 -d ' ' | sort | uniq -c

    999 Bisulfite-Seq
    768 ChIP-Seq
      1 library_strategy
    121 OTHER
    353 RNA-Seq
     28 WGS

We want to however only download ``RNA-seq`` samples:

::

    $ pysradb metadata SRP000941 --assay | grep 'study\|RNA-Seq' | pysradb download

This will download all ``RNA-seq`` samples coming from this project using ``aspera-client``, if available.
Alternatively, it can also use ``wget``.


Downloading an entire project is easy:

::

    $ pysradb download -p SRP000941

Downloads are organized by ``SRP/SRX/SRR`` mimicking the hiererachy of SRA projects.





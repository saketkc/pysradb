============
Introduction
============


``pysradb`` provides a simple method to programmatically access metadata
and download sequencing data from NCBI's Sequence Read Archive (SRA) and European Bioinformatics
Institute's European Nucleotide Archive (ENA).



=============
Quick Example
=============

To fetch metadata associated with project accession ``SRP265425``

.. code-block:: console

    $ pysradb metadata SRP265425

    study_accession	experiment_accession	experiment_title	experiment_desc	organism_taxid 	organism_name	library_name	library_strategy	library_source	library_selection	library_layout	sample_accession	sample_title	instrument	instrument_model	instrument_model_desc	total_spots	total_size	run_accession	run_total_spots	run_total_bases
    SRP265425	SRX8434255	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	63-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745319		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1311358	83306910	SRR11886735	1311358	109594216
    SRP265425	SRX8434254	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	62-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745320		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	2614109	204278682	SRR11886736	2614109	262305651
    SRP265425	SRX8434253	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	61-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745318		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	2286312	183516004	SRR11886737	2286312	263304134
    SRP265425	SRX8434252	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	60-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745317		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	5202567	507524965	SRR11886738	5202567	781291588
    SRP265425	SRX8434251	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	38-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745315		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	3313960	356104406	SRR11886739	3313960	612430817
    SRP265425	SRX8434250	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	37-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745316		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	5155733	565882351	SRR11886740	5155733	954342917
    SRP265425	SRX8434249	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	36-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745313		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1324589	175619046	SRR11886741	1324589	216531400
    SRP265425	SRX8434248	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	35-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745314		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1639851	198973268	SRR11886742	1639851	245466005
    SRP265425	SRX8434247	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	68-2020-05-07	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745312		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	3921389	210198580	SRR11886743	3921389	332935558
    SRP265425	SRX8434246	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	66-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745311		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	14295475	2150005008	SRR11886744	14295475	2967829315
    SRP265425	SRX8434245	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	65-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745310		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	5124692	294846140	SRR11886745	5124692	431819462
    SRP265425	SRX8434244	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	64-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745309		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	2986306	205666872	SRR11886746	2986306	275400959
    SRP265425	SRX8434243	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	34-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745308		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1182690	59471336	SRR11886747	1182690	86350631
    SRP265425	SRX8434242	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	33-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745307		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	6031816	749323230	SRR11886748	6031816	928054297


To fetch detailed metadata which includes link to raw sequencing files, specify ``--detailed``:

.. code-block:: console

    $ pysradb metadata SRP265425 --detailed

    run_accession	study_accession	experiment_accession	experiment_title	experiment_desc	organism_taxid 	organism_name	library_name	library_strategy	library_source	library_selection	library_layout	sample_accession	sample_title	instrument	instrument_model	instrument_model_desc	total_spots	total_size	run_total_spots	run_total_bases	run_alias	sra_url_alt1	sra_url_alt2	sra_url	experiment_alias	isolate	collected_by	collection_date	geo_loc_name	host	host_disease	isolation_source	lat_lon	BioSampleModel	sra_url_alt3	ena_fastq_http	ena_fastq_http_1	ena_fastq_http_2	ena_fastq_ftp	ena_fastq_ftp_1	ena_fastq_ftp_2
    SRR11886735	SRP265425	SRX8434255	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	63-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745319		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1311358	83306910	1311358	109594216	IonXpress_063_R_2020_04_22_15_56_22_user_GCEID-S5-58-SARS_CoV2_SA4.bam	gs://sra-pub-src-9/SRR11886735/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886735/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra0/SRR/011608/SRR11886735		GC-20	NA	02-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/035/SRR11886735/SRR11886735.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/035/SRR11886735/SRR11886735.fastq.gz
    SRR11886736	SRP265425	SRX8434254	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	62-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745320		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	2614109	204278682	2614109	262305651	IonXpress_062_R_2020_04_22_15_56_22_user_GCEID-S5-58-SARS_CoV2_SA4.bam	gs://sra-pub-src-16/SRR11886736/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra46/SRZ/011886/SRR11886736/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta	https://sra-download.ncbi.nlm.nih.gov/traces/sra50/SRR/011608/SRR11886736		GC-51	NA	14-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886736/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/036/SRR11886736/SRR11886736.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/036/SRR11886736/SRR11886736.fastq.gz
    SRR11886737	SRP265425	SRX8434253	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	61-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745318		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	2286312	183516004	2286312	263304134	IonXpress_061_R_2020_04_22_15_56_22_user_GCEID-S5-58-SARS_CoV2_SA4.bam	gs://sra-pub-src-16/SRR11886737/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra29/SRZ/011886/SRR11886737/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta	https://sra-download.ncbi.nlm.nih.gov/traces/sra17/SRR/011608/SRR11886737		GC-24	NA	07-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886737/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/037/SRR11886737/SRR11886737.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/037/SRR11886737/SRR11886737.fastq.gz
    SRR11886738	SRP265425	SRX8434252	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	60-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745317		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	5202567	507524965	5202567	781291588	IonXpress_060_R_2020_04_22_15_56_22_user_GCEID-S5-58-SARS_CoV2_SA4.bam	gs://sra-pub-src-15/SRR11886738/IonXpress_060_R_2020_04_22_15_56_22_user_GCEID_S5_58_SARS_CoV2_SA4.bam.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra69/SRZ/011886/SRR11886738/IonXpress_060_R_2020_04_22_15_56_22_user_GCEID_S5_58_SARS_CoV2_SA4.bam	https://sra-download.ncbi.nlm.nih.gov/traces/sra77/SRR/011608/SRR11886738		GC-23	NA	08-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886738/IonXpress_060_R_2020_04_22_15_56_22_user_GCEID_S5_58_SARS_CoV2_SA4.bam.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/038/SRR11886738/SRR11886738.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/038/SRR11886738/SRR11886738.fastq.gz
    SRR11886739	SRP265425	SRX8434251	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	38-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745315		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	3313960	356104406	3313960	612430817	IonXpress_038_R_2020_04_03_10_09_05_user_GCEID-S5-55-SARS_CoV2_SA4.bam	gs://sra-pub-src-13/SRR11886739/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886739/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra24/SRR/011608/SRR11886739		GC-11b	NA	24-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/039/SRR11886739/SRR11886739.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/039/SRR11886739/SRR11886739.fastq.gz
    SRR11886740	SRP265425	SRX8434250	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	37-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745316		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	5155733	565882351	5155733	954342917	IonXpress_037_R_2020_04_03_10_09_05_user_GCEID-S5-55-SARS_CoV2_SA4.bam	gs://sra-pub-src-5/SRR11886740/IonXpress_037_R_2020_04_03_10_09_05_user_GCEID_S5_55_SARS_CoV2_SA4.bam.1	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886740/IonXpress_037_R_2020_04_03_10_09_05_user_GCEID_S5_55_SARS_CoV2_SA4.bam.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra13/SRR/011608/SRR11886740		GC-14b	NA	28-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/040/SRR11886740/SRR11886740.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/040/SRR11886740/SRR11886740.fastq.gz
    SRR11886741	SRP265425	SRX8434249	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	36-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745313		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1324589	175619046	1324589	216531400	IonXpress_036_R_2020_04_03_10_09_05_user_GCEID-S5-55-SARS_CoV2_SA4.bam	gs://sra-pub-src-11/SRR11886741/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886741/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra57/SRR/011608/SRR11886741		GC-12	NA	24-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/041/SRR11886741/SRR11886741.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/041/SRR11886741/SRR11886741.fastq.gz
    SRR11886742	SRP265425	SRX8434248	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	35-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745314		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1639851	198973268	1639851	245466005	IonXpress_035_R_2020_04_03_10_09_05_user_GCEID-S5-55-SARS_CoV2_SA4.bam	gs://sra-pub-src-11/SRR11886742/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886742/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra69/SRR/011608/SRR11886742		GC-13	NA	23-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/042/SRR11886742/SRR11886742.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/042/SRR11886742/SRR11886742.fastq.gz
    SRR11886743	SRP265425	SRX8434247	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	68-2020-05-07	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745312		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	3921389	210198580	3921389	332935558	IonXpress_068_R_2020_05_07_11_47_51_user_GCEID-S5-60-SARS_CoV2_SA4.bam	gs://sra-pub-src-17/SRR11886743/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra64/SRZ/011886/SRR11886743/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta	https://sra-download.ncbi.nlm.nih.gov/traces/sra54/SRR/011608/SRR11886743		GC-55	NA	24-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886743/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/043/SRR11886743/SRR11886743.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/043/SRR11886743/SRR11886743.fastq.gz
    SRR11886744	SRP265425	SRX8434246	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	66-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745311		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	14295475	2150005008	14295475	2967829315	IonXpress_066_R_2020_04_22_11_10_56_user_GCEID-S5-57-SARS_CoV2_SA4.fastq	gs://sra-pub-src-11/SRR11886744/IonXpress_066_R_2020_04_22_11_10_56_user_GCEID-S5-57-SARS_CoV2_SA4.fastq.1	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886744/IonXpress_066_R_2020_04_22_11_10_56_user_GCEID-S5-57-SARS_CoV2_SA4.fastq.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra20/SRR/011608/SRR11886744		GC-26	NA	07-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/044/SRR11886744/SRR11886744.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/044/SRR11886744/SRR11886744.fastq.gz
    SRR11886745	SRP265425	SRX8434245	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	65-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745310		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	5124692	294846140	5124692	431819462	IonXpress_065_R_2020_04_22_11_10_56_user_GCEID-S5-57-SARS_CoV2_SA4.bam	gs://sra-pub-src-16/SRR11886745/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra69/SRZ/011886/SRR11886745/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta	https://sra-download.ncbi.nlm.nih.gov/traces/sra19/SRR/011608/SRR11886745		GC-25	NA	10-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886745/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/045/SRR11886745/SRR11886745.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/045/SRR11886745/SRR11886745.fastq.gz
    SRR11886746	SRP265425	SRX8434244	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	64-2020-04-22	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745309		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	2986306	205666872	2986306	275400959	IonXpress_064_R_2020_04_22_15_56_22_user_GCEID-S5-58-SARS_CoV2_SA4.bam	gs://sra-pub-src-17/SRR11886746/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra59/SRZ/011886/SRR11886746/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta	https://sra-download.ncbi.nlm.nih.gov/traces/sra47/SRR/011608/SRR11886746		GC-21	NA	03-Apr-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886746/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/046/SRR11886746/SRR11886746.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/046/SRR11886746/SRR11886746.fastq.gz
    SRR11886747	SRP265425	SRX8434243	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	34-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745308		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	1182690	59471336	1182690	86350631	IonXpress_034_R_2020_04_03_10_09_05_user_GCEID-S5-55-SARS_CoV2_SA4.bam	gs://sra-pub-src-16/SRR11886747/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra77/SRZ/011886/SRR11886747/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta	https://sra-download.ncbi.nlm.nih.gov/traces/sra13/SRR/011608/SRR11886747		GC-11a	NA	24-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886747/Wuhan_Hu_1_NC_045512_21500_and_subgenomics_SA4.fasta.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/047/SRR11886747/SRR11886747.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/047/SRR11886747/SRR11886747.fastq.gz
    SRR11886748	SRP265425	SRX8434242	Ampliseq of SARS-CoV-2	Ampliseq of SARS-CoV-2	2697049	Severe acute respiratory syndrome coronavirus 2	33-2020-04-03	AMPLICON	VIRAL RNA	RT-PCR	SINGLE	SRS6745307		Ion Torrent S5 XL	Ion Torrent S5 XL	ION_TORRENT	6031816	749323230	6031816	928054297	IonXpress_033_R_2020_04_03_10_09_05_user_GCEID-S5-55-SARS_CoV2_SA4.bam	gs://sra-pub-src-15/SRR11886748/IonXpress_033_R_2020_04_03_10_09_05_user_GCEID_S5_55_SARS_CoV2_SA4.bam.1	https://sra-download.ncbi.nlm.nih.gov/traces/sra43/SRZ/011886/SRR11886748/IonXpress_033_R_2020_04_03_10_09_05_user_GCEID_S5_55_SARS_CoV2_SA4.bam	https://sra-download.ncbi.nlm.nih.gov/traces/sra66/SRR/011608/SRR11886748		GC-14a	NA	28-Mar-2020	Australia: Victoria	Homo sapiens	COVID-19	swab	NA	Pathogen.cl	https://sra-pub-sars-cov2.s3.amazonaws.com/sra-src/SRR11886748/IonXpress_033_R_2020_04_03_10_09_05_user_GCEID_S5_55_SARS_CoV2_SA4.bam.1	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR118/048/SRR11886748/SRR11886748.fastq.gz			era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR118/048/SRR11886748/SRR11886748.fastq.gz

See :doc:`quickstart` for other examples.

===========================================================================

========
Contents
========

.. toctree::
   :maxdepth: 1

   installation
   quickstart
   cmdline
   python-api-usage
   case_studies
   commands
   contributing
   authors
   history
   modules


===========================================================================


===========
Publication
===========

 `pysradb: A Python package to query next-generation sequencing metadata and data from NCBI Sequence Read Archive <https://f1000research.com/articles/8-532/v1>`_


 Presentation slides from BOSC (ISMB-ECCB) 2019: https://f1000research.com/slides/8-1183

===========================================================================

========
Citation
========

Choudhary, Saket. "pysradb: A Python Package to Query next-Generation Sequencing Metadata and Data from NCBI Sequence Read Archive." F1000Research, vol. 8, F1000 (Faculty of 1000 Ltd), Apr. 2019, p. 532 (https://f1000research.com/articles/8-532/v1)

::

    @article{Choudhary2019,
    doi = {10.12688/f1000research.18676.1},
    url = {https://doi.org/10.12688/f1000research.18676.1},
    year = {2019},
    month = apr,
    publisher = {F1000 (Faculty of 1000 Ltd)},
    volume = {8},
    pages = {532},
    author = {Saket Choudhary},
    title = {pysradb: A {P}ython package to query next-generation sequencing metadata and data from {NCBI} {S}equence {R}ead {A}rchive},
    journal = {F1000Research}
    }


Zenodo archive: https://zenodo.org/badge/latestdoi/159590788

Zenodo DOI: 10.5281/zenodo.2306881

===========================================================================

==========
Questions?
==========

Join our `Slack Channel <https://join.slack.com/t/pysradb/shared_invite/zt-f01jndpy-KflPu3Be5Aq3FzRh5wj1Ug>`_ or open an `issue <https://github.com/saketkc/pysradb/issues>`_.


==================
Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

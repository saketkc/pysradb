.. _usagescenarios:

#############
Case Studies
#############


=============
Case Study 1
=============

Consider a scenario where somone is interested in searching for single-cell
RNA-seq datasets. In particular, the interest is in studying retina:


::

   $ pysradb search --query "single-cell rna-seq retina"

    study_accession	experiment_accession	experiment_title	sample_taxon_id	sample_scientific_name	experiment_library_strategy	experiment_library_source	experiment_library_selection	sample_accession	sample_alias	experiment_instrument_model	pool_member_spots	run_1_size	run_1_accession	run_1_total_spots	run_1_total_bases
    SRP299803	SRX9756769	GSM4995565: scATAC_Retina_WT; Mus musculus; ATAC-seq	10090	Mus musculus	ATAC-seq	GENOMIC	other	SRS7946094	GSM4995565	Illumina NovaSeq 6000	55435867	2637580797	SRR13329759	55435867	6874047508
    SRP299803	SRX9756768	GSM4995564: scRNA_Retina_VSX2SEKO_Rep2; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7946093	GSM4995564	Illumina NovaSeq 6000	96123725	4107807391	SRR13329758	96123725	12688331700
    SRP299803	SRX9756767	GSM4995563: scRNA_Retina_VSX2SEKO_Rep1; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7946092	GSM4995563	Illumina NovaSeq 6000	94345783	4056010488	SRR13329757	94345783	12453643356
    SRP299803	SRX9756766	GSM4995562: scRNA_Retina_WT_Rep2; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7946091	GSM4995562	Illumina NovaSeq 6000	99487074	4240172698	SRR13329756	99487074	13132293768
    SRP299803	SRX9756765	GSM4995561: scRNA_Retina_WT_Rep1; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7946090	GSM4995561	Illumina NovaSeq 6000	88048461	3817540828	SRR13329755	88048461	11622396852
    SRP257758	SRX9537754	GSM4916438: Pou4f2-tdTomato/+ E17.5 scRNA-seq; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7743995	GSM4916438	Illumina HiSeq 2500	364683840	8246658699	SRR13091939	364683840	32456861760
    SRP257758	SRX9537753	GSM4916437: Atoh7-zsGreen/lacZ E17.5 scRNA-seq; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7743994	GSM4916437	Illumina HiSeq 2500	530456067	11895864680	SRR13091938	530456067	47210589963
    SRP257758	SRX9537752	GSM4916436: Atoh7-zsGreen/+ E17.5 scRNA-seq; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7743993	GSM4916436	Illumina HiSeq 2500	389849416	8671923722	SRR13091937	389849416	34696598024
    SRP257758	SRX9537751	GSM4916435: Atoh7-zsGreen/lacZ E14.5 scRNA-seq; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7743992	GSM4916435	Illumina HiSeq 2500	328878355	7875737709	SRR13091936	328878355	29270173595
    SRP257758	SRX9537750	GSM4916434: Atoh7-zsGreen/+ E14.5 scRNA-seq; Mus musculus; RNA-Seq	10090	Mus musculus	RNA-Seq	TRANSCRIPTOMIC	cDNA	SRS7743991	GSM4916434	Illumina HiSeq 2500	522040155	12760941656	SRR13091935	522040155	46461573795
    ERP118072	ERX3614517	NextSeq 500 sequencing; 3' mRNA-seq of protrusions and cell bodies of BJ, PC-3M, RPE-1, U-87 and WM-266.4 cells	9606	Homo sapiens	OTHER	TRANSCRIPTOMIC	Oligo-dT	ERS3920269	SAMEA6120013	NextSeq 500	5818488	43355751	ERR3619129	1457318	109897743
    ERP118072	ERX3614516	NextSeq 500 sequencing; 3' mRNA-seq of protrusions and cell bodies of BJ, PC-3M, RPE-1, U-87 and WM-266.4 cells	9606	Homo sapiens	OTHER	TRANSCRIPTOMIC	Oligo-dT	ERS3920268	SAMEA6120012	NextSeq 500	5422441	40645479	ERR3619125	1359663	102468758
    SRP288715	SRX9369597	RPE1_SS119_p10	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591452	RPE1_SS119_p10.bam	Illumina HiSeq 2000	5062938	88426773	SRR12904705	5062938	202517520
    SRP288715	SRX9369596	RPE1_SS119_p0	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591451	RPE1_SS119_p0.bam	Illumina HiSeq 2000	978835	19219630	SRR12904706	978835	39153400
    SRP288715	SRX9369595	RPE1_SS111_p10	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591450	RPE1_SS111_p10.bam	Illumina HiSeq 2000	6205827	108129733	SRR12904707	6205827	248233080
    SRP288715	SRX9369594	RPE1_SS111_p0	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591449	RPE1_SS111_p0.bam	Illumina HiSeq 2000	928703	18488436	SRR12904708	928703	37148120
    SRP288715	SRX9369593	RPE1_SS51_p10	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591448	RPE1_SS51_p10.bam	Illumina HiSeq 2000	6088168	106065537	SRR12904709	6088168	243526720
    SRP288715	SRX9369592	RPE1_SS51_p0	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591447	RPE1_SS51_p0.bam	Illumina HiSeq 2000	1624227	30610200	SRR12904710	1624227	64969080
    SRP288715	SRX9369591	RPE1_SS48_p10	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591446	RPE1_SS48_p10.bam	Illumina HiSeq 2000	8117881	139408135	SRR12904711	8117881	324715240
    SRP288715	SRX9369590	RPE1_SS48_p0	9606	Homo sapiens	OTHER	GENOMIC	other	SRS7591445	RPE1_SS48_p0.bam	Illumina HiSeq 2000	776140	15821200	SRR12904712	776140	31045600

By default search returns first 20 hits. ``SRP299803`` seems like a project of interest. However the information
outputted by the ``search`` command is pretty limited. We want to
look up more detailed information about this project:

::

   $ pysradb metadata SRP299803 | head
    study_accession	experiment_accession	experiment_title	experiment_desc	organism_taxid 	organism_name	library_name	library_strategy	library_source	library_selection	library_layout	sample_accession	sample_title	instrument	instrument_model	instrument_model_desc	total_spots	total_size	run_accession	run_total_spots	run_total_bases
    SRP299803	SRX9756769	GSM4995565: scATAC_Retina_WT; Mus musculus; ATAC-seq	GSM4995565: scATAC_Retina_WT; Mus musculus; ATAC-seq	10090	Mus musculus		ATAC-seq	GENOMIC	other	PAIRED	SRS7946094		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	55435867	2637580797	SRR13329759	55435867	6874047508
    SRP299803	SRX9756768	GSM4995564: scRNA_Retina_VSX2SEKO_Rep2; Mus musculus; RNA-Seq	GSM4995564: scRNA_Retina_VSX2SEKO_Rep2; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946093		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	96123725	4107807391	SRR13329758	96123725	12688331700
    SRP299803	SRX9756767	GSM4995563: scRNA_Retina_VSX2SEKO_Rep1; Mus musculus; RNA-Seq	GSM4995563: scRNA_Retina_VSX2SEKO_Rep1; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946092		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	94345783	4056010488	SRR13329757	94345783	12453643356
    SRP299803	SRX9756766	GSM4995562: scRNA_Retina_WT_Rep2; Mus musculus; RNA-Seq	GSM4995562: scRNA_Retina_WT_Rep2; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946091		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	99487074	4240172698	SRR13329756	99487074	13132293768
    SRP299803	SRX9756765	GSM4995561: scRNA_Retina_WT_Rep1; Mus musculus; RNA-Seq	GSM4995561: scRNA_Retina_WT_Rep1; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946090		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	88048461	3817540828	SRR13329755	88048461	11622396852


It is also possible to get more detailed information using the ``--detailed`` flag:


::

   $ pysradb metadata SRP075720 --detailed

    run_accession	study_accession	experiment_accession	experiment_title	experiment_desc	organism_taxid 	organism_name	library_name	library_strategy	library_source	library_selection	library_layout	sample_accession	sample_title	instrument	instrument_model	instrument_model_desc	total_spots	total_size	run_total_spots	run_total_bases	run_alias	sra_url	experiment_alias	source_name	strain background	genotype	tissue/cell type	molecule subtype	ena_fastq_http	ena_fastq_http_1	ena_fastq_http_2	ena_fastq_ftp	ena_fastq_ftp_1	ena_fastq_ftp_2
    SRR13329759	SRP299803	SRX9756769	GSM4995565: scATAC_Retina_WT; Mus musculus; ATAC-seq	GSM4995565: scATAC_Retina_WT; Mus musculus; ATAC-seq	10090	Mus musculus		ATAC-seq	GENOMIC	other	PAIRED	SRS7946094		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	55435867	2637580797	55435867	6874047508	GSM4995565_r1	https://sra-download.ncbi.nlm.nih.gov/traces/sra77/SRR/013017/SRR13329759	GSM4995565	wild type_retina	C57BL/6	wild type	retina			http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/059/SRR13329759/SRR13329759_1.fastq.gz	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/059/SRR13329759/SRR13329759_2.fastq.gz		era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/059/SRR13329759/SRR13329759_1.fastq.gz	era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/059/SRR13329759/SRR13329759_2.fastq.gz
    SRR13329758	SRP299803	SRX9756768	GSM4995564: scRNA_Retina_VSX2SEKO_Rep2; Mus musculus; RNA-Seq	GSM4995564: scRNA_Retina_VSX2SEKO_Rep2; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946093		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	96123725	4107807391	96123725	12688331700	GSM4995564_r1	https://sra-download.ncbi.nlm.nih.gov/traces/sra70/SRR/013017/SRR13329758	GSM4995564	Vsx2SE Δ/Δ_retina	C57BL/6	Vsx2SE {delta}/{delta}	retina	3' RNA		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/058/SRR13329758/SRR13329758_1.fastq.gz	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/058/SRR13329758/SRR13329758_2.fastq.gz		era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/058/SRR13329758/SRR13329758_1.fastq.gz	era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/058/SRR13329758/SRR13329758_2.fastq.gz
    SRR13329757	SRP299803	SRX9756767	GSM4995563: scRNA_Retina_VSX2SEKO_Rep1; Mus musculus; RNA-Seq	GSM4995563: scRNA_Retina_VSX2SEKO_Rep1; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946092		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	94345783	4056010488	94345783	12453643356	GSM4995563_r1	https://sra-download.ncbi.nlm.nih.gov/traces/sra79/SRR/013017/SRR13329757	GSM4995563	Vsx2SE Δ/Δ_retina	C57BL/6	Vsx2SE {delta}/{delta}	retina	3' RNA		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/057/SRR13329757/SRR13329757_1.fastq.gz	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/057/SRR13329757/SRR13329757_2.fastq.gz		era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/057/SRR13329757/SRR13329757_1.fastq.gz	era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/057/SRR13329757/SRR13329757_2.fastq.gz
    SRR13329756	SRP299803	SRX9756766	GSM4995562: scRNA_Retina_WT_Rep2; Mus musculus; RNA-Seq	GSM4995562: scRNA_Retina_WT_Rep2; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946091		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	99487074	4240172698	99487074	13132293768	GSM4995562_r1	https://sra-download.ncbi.nlm.nih.gov/traces/sra77/SRR/013017/SRR13329756	GSM4995562	wild type_retina	C57BL/6	wild type	retina	3' RNA		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/056/SRR13329756/SRR13329756_1.fastq.gz	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/056/SRR13329756/SRR13329756_2.fastq.gz		era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/056/SRR13329756/SRR13329756_1.fastq.gz	era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/056/SRR13329756/SRR13329756_2.fastq.gz
    SRR13329755	SRP299803	SRX9756765	GSM4995561: scRNA_Retina_WT_Rep1; Mus musculus; RNA-Seq	GSM4995561: scRNA_Retina_WT_Rep1; Mus musculus; RNA-Seq	10090	Mus musculus		RNA-Seq	TRANSCRIPTOMIC	cDNA	PAIRED	SRS7946090		Illumina NovaSeq 6000	Illumina NovaSeq 6000	ILLUMINA	88048461	3817540828	88048461	11622396852	GSM4995561_r1	https://sra-download.ncbi.nlm.nih.gov/traces/sra72/SRR/013017/SRR13329755	GSM4995561	wild type_retina	C57BL/6	wild type	retina	3' RNA		http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/055/SRR13329755/SRR13329755_1.fastq.gz	http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR133/055/SRR13329755/SRR13329755_2.fastq.gz		era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/055/SRR13329755/SRR13329755_1.fastq.gz	era-fasp@fasp.sra.ebi.ac.uk:vol1/fastq/SRR133/055/SRR13329755/SRR13329755_2.fastq.gz


Having made sure this dataset is indeed of interest, we want to save some work and see
if the processed dataset has been made available on GEO by the authors:

::

    $ pysradb srp-to-gse SRP299803

    study_accession  study_alias
    SRP299803        GSE164044

So indeed a GEO project exists for this SRA dataset.


Notice, that the GEO information was also visible in the ``metadata --detailed`` operation.
Assume we were in posession of the GSM id of one of the experiments to start off with, say
``GSE4995565``. Starting from this GSM id, we want to get the following information:

* SRP id of the project
* GSE id of the project
* SRX id of the experiment
* SRR id(s) corresponding to the experiment


Get SRP id:


::

    $ pysradb gsm-to-srp GSM4995565

    experiment_alias study_accession
    GSM4995565       SRP299803


Get GSE id:

::

    $ pysradb gsm-to-gse GSM4995565

    experiment_alias study_alias
    GSM4995565       GSE164044

Get SRX id:

::

    $ pysradb gsm-to-srx GSM4995565

    experiment_alias experiment_accession
    GSM4995565       SRX9756769

Getting SRR id(s):

::

    $ pysradb gsm-to-srr GSM4995565

    experiment_alias run_accession
    GSM4995565       SRR13329759


=============
Case Study 2
=============

Our first case study included metadata search. Next, we explore downloading datasets.

We have a SRP id to start off with: ``SRP000941``. We want to
quickly checkout its contents:

::

    $ pysradb metadata SRP000941 --detailed| head

    study_accession	experiment_accession	experiment_title	experiment_desc	organism_taxid 	organism_name	library_name	library_strategy	library_source	library_selection	library_layout	sample_accession	sample_title	instrument	instrument_model	instrument_model_desc	total_spots	total_size	run_accession	run_total_spots	run_total_bases
    SRP000941	SRX056722	Reference Epigenome: ChIP-Seq Analysis of H3K27ac in hESC H1 Cells	Reference Epigenome: ChIP-Seq Analysis of H3K27ac in hESC H1 Cells	9606	Homo sapiens	SAK270	ChIP-Seq	GENOMIC	ChIP	SINGLE	SRS184466		Illumina HiSeq 2000	Illumina HiSeq 2000	ILLUMINA	26900401	531654480	SRR179707	26900401	807012030
    SRP000941	SRX027889	Reference Epigenome: ChIP-Seq Analysis of H2AK5ac in hESC Cells	Reference Epigenome: ChIP-Seq Analysis of H2AK5ac in hESC Cells	9606	Homo sapiens	SAK201	ChIP-Seq	GENOMIC	ChIP	SINGLE	SRS116481		Illumina Genome Analyzer II	Illumina Genome Analyzer II	ILLUMINA	37528590	779578968	SRR067978	37528590	1351029240
    SRP000941	SRX027888	Reference Epigenome: ChIP-Seq Input from hESC H1 Cells	Reference Epigenome: ChIP-Seq Input from hESC H1 Cells	9606	Homo sapiens	LLH1U	ChIP-Seq	GENOMIC	RANDOM	SINGLE	SRS116483		Illumina Genome Analyzer II	Illumina Genome Analyzer II	ILLUMINA	13603127	3232309537	SRR067977	13603127	489712572
    SRP000941	SRX027887	Reference Epigenome: ChIP-Seq Input from hESC H1 Cells	Reference Epigenome: ChIP-Seq Input from hESC H1 Cells	9606	Homo sapiens	DM219	ChIP-Seq	GENOMIC	RANDOM	SINGLE	SRS116562		Illumina Genome Analyzer II	Illumina Genome Analyzer II	ILLUMINA	22430523	506327844	SRR067976	22430523	807498828


This project is a collection of multiple assays.

::

    $ pysradb metadata SRP000941 --detailed  | tr -s '  ' | cut -f5 -d ' ' | sort | uniq -c

    999 Bisulfite-Seq
    768 ChIP-Seq
      1 library_strategy
    121 OTHER
    353 RNA-Seq
     28 WGS

We want to however only download ``RNA-seq`` samples:

::

    $ pysradb metadata SRP000941 --detailed | grep 'study\|RNA-Seq' | pysradb download

This will download all ``RNA-seq`` samples coming from this project using ``aspera-client``, if available.
Alternatively, it can also use ``wget``.


Downloading an entire project is easy:

::

    $ pysradb download -p SRP000941

Downloads are organized by ``SRP/SRX/SRR`` mimicking the hiererachy of SRA projects.

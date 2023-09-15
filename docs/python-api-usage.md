# Python API 

## Use Case 1: Fetch the metadata table (SRA-runtable)

The simplest use case of [pysradb]{.title-ref} is when you know the SRA
project ID (SRP) and would simply want to fetch the metadata associated
with it. This is generally reflected in the
[SraRunTable.txt]{.title-ref} that you get from NCBI\'s website. See an
[example](https://www.ncbi.nlm.nih.gov/Traces/study/?acc=SRP098789) of a
SraRunTable.

``` python
from pysradb import SRAweb
db = SRAweb()
df = db.sra_metadata('SRP098789')
df.head()
```

    ===============  ====================  ======================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========  ============  ===============
    study_accession  experiment_accession                             experiment_title                             run_accession  taxon_id  library_selection  library_layout  library_strategy  library_source  library_name    bases      spots    adapter_spec  avg_read_length
    ===============  ====================  ======================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========  ============  ===============
    SRP098789        SRX2536403            GSM2475997: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER  SRR5227288         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2104142750  42082855                             50
    SRP098789        SRX2536404            GSM2475998: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER  SRR5227289         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2082873050  41657461                             50
    SRP098789        SRX2536405            GSM2475999: 1.5 Ã‚ÂµM PF-067446846, 10 min, rep 3; Homo sapiens; OTHER  SRR5227290         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2023148650  40462973                             50
    SRP098789        SRX2536406            GSM2476000: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 1; Homo sapiens; OTHER  SRR5227291         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                2057165950  41143319                             50
    SRP098789        SRX2536407            GSM2476001: 0.3 Ã‚ÂµM PF-067446846, 10 min, rep 2; Homo sapiens; OTHER  SRR5227292         9606  other              SINGLE -        OTHER             TRANSCRIPTOMIC                3027621850  60552437                             50
    ===============  ====================  ======================================================================  =============  ========  =================  ==============  ================  ==============  ============  ==========  ========  ============  ===============

The metadata is returned as a [pandas]{.title-ref} dataframe and hence
allows you to perform all regular select/query operations available
through [pandas]{.title-ref}.

## Use Case 2: Downloading an entire project arranged experiment wise

Once you have fetched the metadata and made sure, this is the project
you were looking for, you would want to download everything at once.
NCBI follows this hiererachy: [SRP =\> SRX =\> SRR]{.title-ref}. Each
[SRP]{.title-ref} (project) has multiple [SRX]{.title-ref} (experiments)
and each [SRX]{.title-ref} in turn has multiple [SRR]{.title-ref} (runs)
inside it. We want to mimick this hiereachy in our downloads. The reason
to do that is simple: in most cases you care about [SRX]{.title-ref} the
most, and would want to \"merge\" your SRRs in one way or the other.
Having this hierearchy ensures your downstream code can handle such
cases easily, without worrying about which runs (SRR) need to be merged.

We strongly recommend installing [aspera-client]{.title-ref} which uses
UDP and is [designed to be faster](http://www.skullbox.net/tcpudp.php).

``` python
from pysradb import SRAweb
db = SRAweb()
df = db.sra_metadata('SRP017942')
db.download(df)
```

## Use Case 3: Downloading a subset of experiments

Often, you need to process only a smaller set of samples from a project
(SRP). Consider this project which has data spanning four assays.

``` python
df = db.sra_metadata('SRP000941')
print(df.library_strategy.unique())
['ChIP-Seq' 'Bisulfite-Seq' 'RNA-Seq' 'WGS' 'OTHER']
```

But, you might be only interested in analyzing the [RNA-seq]{.title-ref}
samples and would just want to download that subset. This is simple
using [pysradb]{.title-ref} since the metadata can be subset just as you
would subset a dataframe in pandas.

``` python
df_rna = df[df.library_strategy == 'RNA-Seq']
db.download(df=df_rna, out_dir='/pysradb_downloads')()
```

## Use Case 4: Getting cell-type/treatment information from sample_attributes

Cell type/tissue informations is usually hidden in the
[sample_attributes]{.title-ref} column, which can be expanded:

``` python
from pysradb.filter_attrs import expand_sample_attribute_columns
df = db.sra_metadata('SRP017942')
expand_sample_attribute_columns(df).head()
```

<table>
<thead>
<tr class="header">
<th>study_accession</th>
<th>experiment_accession</th>
<th>experiment_title</th>
<th>experiment_attribute</th>
<th>sample_attribute</th>
<th>run_accession</th>
<th>taxon_id</th>
<th>library_selection</th>
<th>library_layout</th>
<th>library_strategy</th>
<th>library_source</th>
<th>library_name</th>
<th>bases</th>
<th>spots</th>
<th>adapter_spec</th>
<th>avg_read_length</th>
<th>assay_type</th>
<th>cell_line</th>
<th>source_name</th>
<th>transfected_with</th>
<th>treatment</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><p>SRP017942 SRP017942 SRP017942 SRP017942 SRP017942</p></td>
<td><p>SRX217028 SRX217029 SRX217030 SRX217031 SRX217956</p></td>
<td><p>GSM1063575: 293T_GFP; Homo sapiens; RNA-Seq GSM1063576:
293T_GFP_2hrs_severe_Heat_Shock; Homo sapiens; RNA-Seq GSM1063577:
293T_Hspa1a; Homo sapiens; RNA-Seq GSM1063578:
293T_Hspa1a_2hrs_severe_Heat_Shock; Homo sapiens; RNA-Seq GSM794854:
3T3-Control-Riboseq; Mus musculus; RNA-Seq</p></td>
<td><p>GEO Accession: GSM1063575 GEO Accession: GSM1063576 GEO
Accession: GSM1063577 GEO Accession: GSM1063578 GEO Accession:
GSM794854</p></td>
<td><p>source_name: 293T cells || cell line: 293T cells || transfected
with: 3XFLAG-GFP || assay type: Riboseq source_name: 293T cells || cell
line: 293T cells || transfected with: 3XFLAG-GFP || treatment: severe
heat shock (44C 2 hours) || assay type: Riboseq source_name: 293T cells
|| cell line: 293T cells || transfected with: 3XFLAG-Hspa1a || assay
type: Riboseq source_name: 293T cells || cell line: 293T cells ||
transfected with: 3XFLAG-Hspa1a || treatment: severe heat shock (44C 2
hours) || assay type: Riboseq source_name: 3T3 cells || treatment:
control || cell line: 3T3 cells || assay type: Riboseq</p></td>
<td><p>SRR648667 SRR648668 SRR648669 SRR648670 SRR649752</p></td>
<td><blockquote>
<p>9606 9606 9606 9606 10090</p>
</blockquote></td>
<td><p>other other other other cDNA</p></td>
<td><p>SINGLE -SINGLE -SINGLE -SINGLE -SINGLE -</p></td>
<td><p>RNA-Seq RNA-Seq RNA-Seq RNA-Seq RNA-Seq</p></td>
<td><p>TRANSCRIPTOMIC TRANSCRIPTOMIC TRANSCRIPTOMIC TRANSCRIPTOMIC
TRANSCRIPTOMIC</p></td>
<td></td>
<td><p>1806641316 3436984836 3330909216 3622123512 594945396</p></td>
<td><blockquote>
<p>50184481 95471801 92525256</p>
</blockquote>
<dl>
<dt>100614542</dt>
<dd>
<p>16526261</p>
</dd>
</dl></td>
<td></td>
<td><blockquote>
<p>36 36 36 36 36</p>
</blockquote></td>
<td><p>riboseq riboseq riboseq riboseq riboseq</p></td>
<td><p>293t cells 293t cells 293t cells 293t cells 3t3 cells</p></td>
<td><p>293t cells 293t cells 293t cells 293t cells 3t3 cells</p></td>
<td><p>3xflag-gfp 3xflag-gfp 3xflag-hspa1a 3xflag-hspa1a NaN</p></td>
<td><p>NaN severe heat shock (44c 2 hours) NaN severe heat shock (44c 2
hours) control</p></td>
</tr>
</tbody>
</table>

## Use Case 5: Searching for datasets

Another common operation that we do on SRA is seach, plain text search.

If you want to look up for all projects where [ribosome
profiling]{.title-ref} appears somewhere in the description:

``` python
df = db.search_sra(search_str='"ribosome profiling"')
df.head()
```

<table>
<thead>
<tr class="header">
<th>study_accession</th>
<th>experiment_accession</th>
<th>experiment_title</th>
<th>run_accession</th>
<th>taxon_id</th>
<th>library_selection</th>
<th>library_layout</th>
<th>library_strategy</th>
<th>library_source</th>
<th>library_name</th>
<th>bases</th>
<th>spots</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>DRP003075</td>
<td>DRX019536</td>
<td>Illumina Genome Analyzer IIx sequencing of SAMD00018584</td>
<td>DRR021383</td>
<td><blockquote>
<p>83333</p>
</blockquote></td>
<td>other</td>
<td>SINGLE -</td>
<td>OTHER</td>
<td>TRANSCRIPTOMIC</td>
<td>GAII05_3</td>
<td><blockquote>
<p>978776480</p>
</blockquote></td>
<td>12234706</td>
</tr>
<tr class="even">
<td>DRP003075</td>
<td>DRX019537</td>
<td>Illumina Genome Analyzer IIx sequencing of SAMD00018585</td>
<td>DRR021384</td>
<td><blockquote>
<p>83333</p>
</blockquote></td>
<td>other</td>
<td>SINGLE -</td>
<td>OTHER</td>
<td>TRANSCRIPTOMIC</td>
<td>GAII05_4</td>
<td><blockquote>
<p>894201680</p>
</blockquote></td>
<td>11177521</td>
</tr>
<tr class="odd">
<td>DRP003075</td>
<td>DRX019538</td>
<td>Illumina Genome Analyzer IIx sequencing of SAMD00018586</td>
<td>DRR021385</td>
<td><blockquote>
<p>83333</p>
</blockquote></td>
<td>other</td>
<td>SINGLE -</td>
<td>OTHER</td>
<td>TRANSCRIPTOMIC</td>
<td>GAII05_5</td>
<td><blockquote>
<p>931536720</p>
</blockquote></td>
<td>11644209</td>
</tr>
<tr class="even">
<td>DRP003075</td>
<td>DRX019540</td>
<td>Illumina Genome Analyzer IIx sequencing of SAMD00018588</td>
<td>DRR021387</td>
<td><blockquote>
<p>83333</p>
</blockquote></td>
<td>other</td>
<td>SINGLE -</td>
<td>OTHER</td>
<td>TRANSCRIPTOMIC</td>
<td>GAII07_4</td>
<td>2759398700</td>
<td>27593987</td>
</tr>
<tr class="odd">
<td>DRP003075</td>
<td>DRX019541</td>
<td>Illumina Genome Analyzer IIx sequencing of SAMD00018589</td>
<td>DRR021388</td>
<td><blockquote>
<p>83333</p>
</blockquote></td>
<td>other</td>
<td>SINGLE -</td>
<td>OTHER</td>
<td>TRANSCRIPTOMIC</td>
<td>GAII07_5</td>
<td>2386196500</td>
<td>23861965</td>
</tr>
</tbody>
</table>

Again, the results are available as a [pandas]{.title-ref} dataframe and
hence you can perform all subset operations post your query. Your query
doesn\'t need to be exact.

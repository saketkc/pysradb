# MCP server

`pysradb` can expose read-oriented metadata workflows through the Model Context
Protocol (MCP). This lets an MCP-capable assistant call `pysradb` tools directly
instead of scraping documentation or constructing shell commands.

## Install

MCP support is optional:

```bash
python -m pip install "pysradb[mcp]"
```

For local development:

```bash
python -m pip install --editable ".[mcp]"
```

## Local stdio usage

You do not need to deploy a hosted server. MCP uses the word "server" for the
tool-providing process, but the default `pysradb` setup is a local stdio
subprocess. Your MCP client starts the command and communicates with it over
standard input and standard output.

```bash
pysradb-mcp
```

This is equivalent to:

```bash
pysradb-mcp --transport stdio
```

Use your MCP client's configuration to run `pysradb-mcp` as a local command.
For clients that accept JSON configuration, the command usually looks like this:

```json
{
  "mcpServers": {
    "pysradb": {
      "command": "pysradb-mcp",
      "args": []
    }
  }
}
```

For a development checkout, run the editable install first:

```bash
python -m pip install --editable ".[mcp]"
```

## HTTP transport

For experimentation or hosted deployments, the same server can run with
streamable HTTP:

```bash
pysradb-mcp --transport streamable-http
```

Most users should prefer stdio unless they have a specific reason to expose an
HTTP endpoint.

## Exposed tools

The MCP server exposes bounded, read-oriented tools. Use `list_capabilities` from
an MCP client to see the complete tool list and the workflows intentionally
omitted from MCP.

### Metadata and search

- `list_capabilities`: list tools, supported conversion pairs, result caps, and omitted side-effecting workflows.
- `get_metadata`: fetch SRA or GEO metadata for SRP or GSE accessions.
- `get_sra_metadata`: fetch SRA metadata for SRP, SRR, SRX, SRS, GSM, or related accessions.
- `get_geo_metadata`: fetch GEO metadata for GSE accessions.
- `get_gds_results`: fetch NCBI GEO DataSets summary results for a GSE accession.
- `get_gsm_soft_metadata`: fetch parsed GEO SOFT metadata for GSM accessions.
- `search_datasets`: search SRA, ENA, or GEO.

### Accessions and file URL discovery

- `map_publication_identifiers`: map SRP, GSE, PMID, PMC, or DOI identifiers.
- `convert_accession`: convert between common GSE, GSM, SRP, SRX, SRS, and SRR accessions.
- `convert_bioproject_to_srp`: convert PRJNA BioProject IDs to SRP accessions.
- `get_ena_fastq_urls`: fetch ENA FASTQ URLs without downloading files.
- `get_geo_supplementary_links`: list GEO supplementary file links without downloading files.
- `get_geo_matrix_url`: construct the GEO Series Matrix URL without downloading it.

### Publications and identifiers

- `get_publication_info`: get metadata and journal metrics for PMIDs, PMCIDs, or DOIs.
- `get_publication_metadata`: fetch publication metadata for PMIDs.
- `get_pmids_for_bioproject`: fetch PMIDs associated with BioProject accessions.
- `get_pmids_for_sra_accession`: fetch PMIDs for SRP, SRR, SRX, SRS, or other SRA accessions.
- `get_pmids_for_gse`: fetch PMIDs for GSE accessions.
- `get_pmids_for_arrayexpress`: fetch PMIDs for ArrayExpress accessions.
- `get_pmids_for_ena_or_bioproject`: fetch PMIDs for ENA or BioProject accessions.
- `convert_doi_to_pmid`: convert DOIs to PMIDs.
- `convert_pmid_to_pmc`: convert PMIDs to PMC IDs.
- `get_identifiers_from_pmc`: extract GSE, PRJNA, SRP, SRR, SRX, and SRS identifiers from PMC articles.
- `get_identifiers_from_pmid`: extract dataset identifiers from PubMed articles via PMC links.
- `get_identifiers_from_doi`: extract dataset identifiers from DOI-linked articles.
- `get_gse_from_pmid`: get GSE accessions from PMIDs.
- `get_srp_from_pmid`: get SRP accessions from PMIDs.
- `get_gse_from_doi`: get GSE accessions from DOIs.
- `get_srp_from_doi`: get SRP accessions from DOIs.
- `search_pmc_for_external_source`: search PMC for PMIDs mentioning an external source such as SRP or GSE.
- `get_pmc_fulltext_excerpt`: fetch a bounded PMC full-text XML excerpt for inspection.
- `extract_identifiers_from_text`: extract dataset identifiers from supplied text without network access.

Each tabular response includes `columns`, `records`, `returned`, `total_rows`,
and `truncated`. Results are capped to avoid accidentally sending very large
tables into an assistant context.

## Safety

Bulk sequencing downloads are intentionally not exposed as MCP tools. Downloading
SRA, ENA, or GEO data can consume substantial disk, bandwidth, and time, so those
workflows should stay explicit through the CLI or Python API.

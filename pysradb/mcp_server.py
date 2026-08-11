"""Model Context Protocol server for pysradb.

The MCP dependency is optional. Install with ``pysradb[mcp]`` before running
the ``pysradb-mcp`` console script.
"""

from __future__ import annotations

import argparse
import math
from typing import Any

import pandas as pd

from . import __version__
from .filter_attrs import expand_sample_attribute_columns
from .geoweb import GEOweb
from .search import EnaSearch, GeoSearch, SraSearch
from .sraweb import SRAweb

MAX_RECORDS_LIMIT = 100
DEFAULT_RECORDS_LIMIT = 20

ACCESSION_CONVERSIONS = {
    "gse_to_gsm",
    "gse_to_srp",
    "gsm_to_gse",
    "gsm_to_srp",
    "gsm_to_srr",
    "gsm_to_srs",
    "gsm_to_srx",
    "srp_to_gse",
    "srp_to_srr",
    "srp_to_srs",
    "srp_to_srx",
    "srr_to_gsm",
    "srr_to_srp",
    "srr_to_srs",
    "srr_to_srx",
    "srs_to_gsm",
    "srs_to_srx",
    "srx_to_gsm",
    "srx_to_srp",
    "srx_to_srr",
    "srx_to_srs",
}

MCP_TOOL_NAMES = [
    "list_capabilities",
    "get_metadata",
    "get_sra_metadata",
    "get_geo_metadata",
    "get_gds_results",
    "get_gsm_soft_metadata",
    "search_datasets",
    "convert_accession",
    "convert_bioproject_to_srp",
    "get_ena_fastq_urls",
    "get_geo_supplementary_links",
    "get_geo_matrix_url",
    "map_publication_identifiers",
    "get_publication_info",
    "get_publication_metadata",
    "get_pmids_for_bioproject",
    "get_pmids_for_sra_accession",
    "get_pmids_for_gse",
    "get_pmids_for_arrayexpress",
    "get_pmids_for_ena_or_bioproject",
    "convert_doi_to_pmid",
    "convert_pmid_to_pmc",
    "get_identifiers_from_pmc",
    "get_identifiers_from_pmid",
    "get_identifiers_from_doi",
    "get_gse_from_pmid",
    "get_srp_from_pmid",
    "get_gse_from_doi",
    "get_srp_from_doi",
    "search_pmc_for_external_source",
    "get_pmc_fulltext_excerpt",
    "extract_identifiers_from_text",
]


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy null-like values into JSON-safe values."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return value


def _limited_records(
    df: pd.DataFrame | None,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Return a compact, JSON-serializable DataFrame payload."""
    if df is None:
        df = pd.DataFrame()

    safe_limit = max(0, min(int(limit), MAX_RECORDS_LIMIT))
    records = df.head(safe_limit).replace({pd.NA: None}).to_dict(orient="records")
    return {
        "columns": list(df.columns),
        "records": _json_safe(records),
        "returned": len(records),
        "total_rows": int(len(df.index)),
        "truncated": len(df.index) > safe_limit,
    }


def _client() -> SRAweb:
    return SRAweb()


def _geo_client() -> GEOweb:
    return GEOweb(verbose=False)


def list_capabilities() -> dict[str, Any]:
    """List the MCP tools and intentionally omitted side-effecting workflows."""
    return {
        "tools": MCP_TOOL_NAMES,
        "accession_conversions": sorted(ACCESSION_CONVERSIONS),
        "search_databases": ["sra", "ena", "geo"],
        "max_records_limit": MAX_RECORDS_LIMIT,
        "omitted_by_design": [
            "bulk_sra_download",
            "bulk_ena_download",
            "geo_file_download",
            "geo_matrix_download",
            "metadata_enrichment_with_local_llm",
        ],
        "omission_reason": (
            "MCP tools are read-oriented. Large downloads and local LLM "
            "enrichment can consume substantial disk, bandwidth, time, or "
            "local compute and should remain explicit CLI/Python workflows."
        ),
    }


def get_metadata(
    accession: str,
    detailed: bool = False,
    include_sample_attributes: bool = False,
    expand_sample_attributes: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Fetch SRA or GEO metadata for an SRP or GSE accession."""
    df = _client().metadata(
        accession,
        detailed=detailed,
        sample_attribute=include_sample_attributes,
    )
    if expand_sample_attributes and "sample_attribute" in df.columns:
        df = expand_sample_attribute_columns(df)
    return _limited_records(df, limit=limit)


def get_sra_metadata(
    srp: str,
    detailed: bool = False,
    include_sample_attributes: bool = False,
    expand_sample_attributes: bool = False,
    include_pmids: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Fetch SRA metadata for SRP, SRR, SRX, SRS, GSM, or related accessions."""
    df = _client().sra_metadata(
        srp,
        detailed=detailed,
        sample_attribute=include_sample_attributes,
        expand_sample_attributes=expand_sample_attributes,
        include_pmids=include_pmids,
    )
    return _limited_records(df, limit=limit)


def get_geo_metadata(
    gse: str,
    detailed: bool = False,
    include_sample_attributes: bool = False,
    expand_sample_attributes: bool = False,
    include_pmids: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Fetch GEO metadata for a GSE accession."""
    df = _client().geo_metadata(
        gse,
        detailed=detailed,
        sample_attribute=include_sample_attributes,
        expand_sample_attributes=expand_sample_attributes,
        include_pmids=include_pmids,
    )
    return _limited_records(df, limit=limit)


def get_gds_results(
    gse: str,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Fetch NCBI GEO DataSets summary results for a GSE accession."""
    return _limited_records(_client().fetch_gds_results(gse), limit=limit)


def get_gsm_soft_metadata(gsm_ids: str) -> dict[str, Any]:
    """Fetch parsed GEO SOFT metadata for one or more GSM accessions."""
    return _json_safe(_client().fetch_gsm_soft(gsm_ids))


def search_datasets(
    query: str,
    db: str = "sra",
    max_results: int = DEFAULT_RECORDS_LIMIT,
    detailed: bool = False,
) -> dict[str, Any]:
    """Search public sequencing metadata in SRA, ENA, or GEO."""
    db = db.lower()
    verbosity = 3 if detailed else 2
    query_terms = [query]

    if db == "sra":
        searcher = SraSearch(verbosity, max_results, query=query_terms)
    elif db == "ena":
        searcher = EnaSearch(verbosity, max_results, query=query_terms)
    elif db == "geo":
        searcher = GeoSearch(verbosity, max_results, query=query_terms)
    else:
        raise ValueError("db must be one of: sra, ena, geo")

    searcher.search()
    return _limited_records(searcher.get_df(), limit=max_results)


def convert_accession(
    accession: str,
    target: str,
    detailed: bool = False,
    include_sample_attributes: bool = False,
    expand_sample_attributes: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Convert between common GEO and SRA accessions."""
    target = target.lower()
    prefix = accession[:3].lower()
    method_name = f"{prefix}_to_{target}"

    if method_name not in ACCESSION_CONVERSIONS:
        raise ValueError(
            "Unsupported conversion. Use a GSE, GSM, SRP, SRR, SRS, or SRX "
            "accession and target one of gse, gsm, srp, srr, srs, or srx."
        )

    method = getattr(_client(), method_name)
    df = method(
        accession,
        detailed=detailed,
        sample_attribute=include_sample_attributes,
        expand_sample_attributes=expand_sample_attributes,
    )
    return _limited_records(df, limit=limit)


def convert_bioproject_to_srp(bioproject: str) -> dict[str, Any]:
    """Convert a PRJNA BioProject accession to matching SRP accessions."""
    return {
        "bioproject": bioproject,
        "srp_accessions": _client().bioproject_to_srp(bioproject),
    }


def get_ena_fastq_urls(srp: str, limit: int = DEFAULT_RECORDS_LIMIT) -> dict[str, Any]:
    """Fetch ENA FASTQ URLs for an SRA project accession without downloading files."""
    urls = _client().fetch_ena_fastq(srp)
    safe_limit = max(0, min(int(limit), MAX_RECORDS_LIMIT))
    return {
        "accession": srp,
        "urls": urls[:safe_limit],
        "returned": len(urls[:safe_limit]),
        "total_urls": len(urls),
        "truncated": len(urls) > safe_limit,
    }


def get_geo_supplementary_links(gse: str) -> dict[str, Any]:
    """List GEO supplementary file links for a GSE accession without downloading."""
    links, root_url = _geo_client().get_download_links(gse)
    return {
        "gse": gse,
        "root_url": root_url,
        "links": links,
        "absolute_urls": [root_url + link for link in links],
    }


def get_geo_matrix_url(accession: str) -> dict[str, str]:
    """Return the GEO Series Matrix URL for a GSE accession without downloading."""
    url = (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/"
        f"{accession[:-3]}nnn/{accession}/matrix/{accession}_series_matrix.txt.gz"
    )
    return {"accession": accession, "url": url}


def map_publication_identifiers(
    identifier: str,
    target: str = "identifiers",
    detailed: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Map SRP, GSE, PMID, PMC, or DOI identifiers to publications or datasets."""
    target = target.lower().replace("-", "_")
    source = identifier.split(":", 1)[0].lower()
    client = _client()

    if identifier.upper().startswith("SRP") and target in {"pmid", "pmids"}:
        df = client.srp_to_pmid(identifier, detailed=detailed)
    elif identifier.upper().startswith("GSE") and target in {"pmid", "pmids"}:
        df = client.gse_to_pmid(identifier, detailed=detailed)
    elif identifier.upper().startswith("PMC") and target == "identifiers":
        df = client.pmc_to_identifiers(identifier)
    elif identifier.isdigit() and target == "identifiers":
        df = client.pmid_to_identifiers(identifier)
    elif identifier.isdigit() and target == "gse":
        df = client.pmid_to_gse(identifier)
    elif identifier.isdigit() and target == "srp":
        df = client.pmid_to_srp(identifier)
    elif source.startswith("10.") or "/" in identifier:
        if target == "identifiers":
            df = client.doi_to_identifiers(identifier)
        elif target == "gse":
            df = client.doi_to_gse(identifier)
        elif target == "srp":
            df = client.doi_to_srp(identifier)
        else:
            raise ValueError("For DOI inputs, target must be identifiers, gse, or srp.")
    else:
        raise ValueError(
            "Unsupported mapping. Use SRP/GSE with target=pmid, PMID with "
            "target=identifiers/gse/srp, PMC with target=identifiers, or DOI "
            "with target=identifiers/gse/srp."
        )

    return _limited_records(df, limit=limit)


def get_publication_info(
    ids: str,
    detailed: bool = False,
    skip_journal_metrics: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Get publication metadata and journal metrics for PMIDs, PMCIDs, or DOIs."""
    df = _client().pmid_info(
        ids,
        detailed=detailed,
        skip_journal_metrics=skip_journal_metrics,
    )
    return _limited_records(df, limit=limit)


def get_publication_metadata(
    pmids: str,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Fetch title, journal, DOI, date, authors, ISSN, and citation counts for PMIDs."""
    return _limited_records(_client().fetch_pmid_metadata(pmids), limit=limit)


def get_pmids_for_bioproject(bioproject: str) -> dict[str, Any]:
    """Fetch PMIDs associated with BioProject accessions."""
    return _json_safe(_client().fetch_bioproject_pmids(bioproject))


def get_pmids_for_sra_accession(
    accession: str,
    detailed: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Get PMIDs for SRP, SRR, SRX, SRS, or other SRA accessions.

    Preprint-only studies have no PMID and report a doi instead.
    """
    client = _client()
    prefix = accession[:3].upper()
    if prefix == "SRP":
        df = client.srp_to_pmid(accession, detailed=detailed)
    elif prefix == "SRR":
        df = client.srr_to_pmid(accession)
    elif prefix == "SRX":
        df = client.srx_to_pmid(accession)
    elif prefix == "SRS":
        df = client.srs_to_pmid(accession)
    else:
        df = client.sra_to_pmid(accession)
    return _limited_records(df, limit=limit)


def get_pmids_for_gse(
    gse: str,
    detailed: bool = False,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Get PMIDs for GSE accessions.

    Preprint-only studies have no PMID and report a doi instead.
    """
    return _limited_records(_client().gse_to_pmid(gse, detailed=detailed), limit=limit)


def get_pmids_for_arrayexpress(
    accession: str,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Get PMIDs for ArrayExpress accessions."""
    return _limited_records(_client().ae_to_pmid(accession), limit=limit)


def get_pmids_for_ena_or_bioproject(
    accession: str,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Get PMIDs for ENA or BioProject accessions such as PRJEB or PRJNA."""
    return _limited_records(_client().ena_to_pmid(accession), limit=limit)


def convert_doi_to_pmid(doi: str) -> dict[str, Any]:
    """Convert DOI identifiers to PMIDs."""
    return _json_safe(_client().doi_to_pmid(doi))


def convert_pmid_to_pmc(pmid: str) -> dict[str, Any]:
    """Convert PMID identifiers to PMC identifiers."""
    return _json_safe(_client().pmid_to_pmc(pmid))


def get_identifiers_from_pmc(
    pmc_id: str,
    convert_missing: bool = True,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Extract GSE, PRJNA, SRP, SRR, SRX, and SRS identifiers from PMC articles."""
    df = _client().pmc_to_identifiers(pmc_id, convert_missing=convert_missing)
    return _limited_records(df, limit=limit)


def get_identifiers_from_pmid(
    pmid: str,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Extract dataset identifiers from PubMed articles via PMC links."""
    return _limited_records(_client().pmid_to_identifiers(pmid), limit=limit)


def get_identifiers_from_doi(
    doi: str,
    limit: int = DEFAULT_RECORDS_LIMIT,
) -> dict[str, Any]:
    """Extract dataset identifiers from DOI-linked articles."""
    return _limited_records(_client().doi_to_identifiers(doi), limit=limit)


def get_gse_from_pmid(pmid: str, limit: int = DEFAULT_RECORDS_LIMIT) -> dict[str, Any]:
    """Get GSE accessions from PMIDs."""
    return _limited_records(_client().pmid_to_gse(pmid), limit=limit)


def get_srp_from_pmid(pmid: str, limit: int = DEFAULT_RECORDS_LIMIT) -> dict[str, Any]:
    """Get SRP accessions from PMIDs."""
    return _limited_records(_client().pmid_to_srp(pmid), limit=limit)


def get_gse_from_doi(doi: str, limit: int = DEFAULT_RECORDS_LIMIT) -> dict[str, Any]:
    """Get GSE accessions from DOIs."""
    return _limited_records(_client().doi_to_gse(doi), limit=limit)


def get_srp_from_doi(doi: str, limit: int = DEFAULT_RECORDS_LIMIT) -> dict[str, Any]:
    """Get SRP accessions from DOIs."""
    return _limited_records(_client().doi_to_srp(doi), limit=limit)


def search_pmc_for_external_source(identifier: str) -> dict[str, Any]:
    """Search PMC for PMIDs mentioning an external source such as SRP or GSE."""
    return {
        "identifier": identifier,
        "pmids": _client().search_pmc_for_external_sources([identifier]),
    }


def get_pmc_fulltext_excerpt(pmc_id: str, char_limit: int = 4000) -> dict[str, Any]:
    """Fetch a bounded PMC full-text XML excerpt for inspection."""
    safe_limit = max(0, min(int(char_limit), 20000))
    text = _client().fetch_pmc_fulltext(pmc_id) or ""
    return {
        "pmc_id": pmc_id if pmc_id.upper().startswith("PMC") else f"PMC{pmc_id}",
        "text": text[:safe_limit],
        "returned_chars": min(len(text), safe_limit),
        "total_chars": len(text),
        "truncated": len(text) > safe_limit,
    }


def extract_identifiers_from_text(text: str) -> dict[str, Any]:
    """Extract dataset identifiers from supplied text without network access."""
    return _client().extract_identifiers_from_text(text)


def create_server():
    """Create and configure the pysradb MCP server."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - exercised without optional dep
        raise RuntimeError(
            "MCP support requires the optional dependency. Install with: "
            'python -m pip install "pysradb[mcp]"'
        ) from exc

    mcp = FastMCP("pysradb")

    @mcp.resource("pysradb://about")
    def about() -> str:
        """Describe this MCP server and its safety constraints."""
        return (
            f"pysradb {__version__} MCP server. Provides read-oriented tools for "
            "SRA, ENA, and GEO metadata search, accession conversion, and "
            "publication identifier mapping. Bulk sequencing downloads are not "
            "exposed as MCP tools."
        )

    for tool in [
        list_capabilities,
        get_metadata,
        get_sra_metadata,
        get_geo_metadata,
        get_gds_results,
        get_gsm_soft_metadata,
        search_datasets,
        convert_accession,
        convert_bioproject_to_srp,
        get_ena_fastq_urls,
        get_geo_supplementary_links,
        get_geo_matrix_url,
        map_publication_identifiers,
        get_publication_info,
        get_publication_metadata,
        get_pmids_for_bioproject,
        get_pmids_for_sra_accession,
        get_pmids_for_gse,
        get_pmids_for_arrayexpress,
        get_pmids_for_ena_or_bioproject,
        convert_doi_to_pmid,
        convert_pmid_to_pmc,
        get_identifiers_from_pmc,
        get_identifiers_from_pmid,
        get_identifiers_from_doi,
        get_gse_from_pmid,
        get_srp_from_pmid,
        get_gse_from_doi,
        get_srp_from_doi,
        search_pmc_for_external_source,
        get_pmc_fulltext_excerpt,
        extract_identifiers_from_text,
    ]:
        mcp.tool()(tool)

    return mcp


def main(argv: list[str] | None = None) -> None:
    """Run the pysradb MCP server."""
    parser = argparse.ArgumentParser(description="Run the pysradb MCP server.")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport to use.",
    )
    args = parser.parse_args(argv)

    server = create_server()
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()

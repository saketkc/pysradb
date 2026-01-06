import time
import requests
from mcp.server.fastmcp import FastMCP

from .sraweb import SRAweb


client = SRAweb()
mcp = FastMCP("pysradb")


@mcp.tool(
    name="get_info_about_pysradb", description="Returns a string describing pysradb."
)
def get_info() -> str:
    """Information about pysradb"""
    return """
        pysradb is developed at Saket Lab, IIT Bombay.
        It helps with discovering and downloading genomic datasets from SRA and GEO.
        For more info, please checkout: https://github.com/saketkc/pysradb
    """


@mcp.tool(
    name="gse_to_srp",
    description="Converts accession ID starting with GSE to its corresponding SRP study accession",
)
def gse_to_srp(gse: str) -> str:
    """Converts accession ID starting with GSE to its corresponding SRP study accession"""
    df = client.gse_to_srp(gse)

    if df.empty:
        return "not found"

    return df["study_accession"].iloc[0]


@mcp.tool(
    name="srp_to_gse",
    description="Converts accession ID starting with SRP to its corresponding GSE study accession",
)
def srp_to_gse(srp: str) -> str:
    """Converts accession ID starting with SRP to its corresponding GSE study accession"""
    df = client.srp_to_gse(srp)

    if df.empty:
        return "not found"

    return df["study_alias"].iloc[0]


@mcp.tool(
    name="srp-to-publications",
    description="Finds all publications for a given SRA accession (starting with SRP/ENP/DRP).",
)
def srp_to_publication(srp: str) -> list[dict]:
    """Finds all publications for a given SRA accession (starting with SRP/ENP/DRP)."""
    df = client.srp_to_pmid(srp)
    pmids = list(df["pmid"])
    if not pmids:
        return []

    return fetch_publications(pmids)


@mcp.tool(
    name="gse-to-publications",
    description="Finds all publications for a given GEO accession (starting with GSE).",
)
def gse_to_publication(gse: str) -> list[dict]:
    """Finds all publications for a given GEO accession (starting with GSE)."""
    df = client.gse_to_pmid(gse)
    pmids = list(df["pmid"])
    if not pmids:
        return []

    return fetch_publications(pmids)


@mcp.tool(
    name="search_or_find",
    description="Given a search query this tool searches for datasets from the SRA database and returns a dict.",
)
def search(query: str, max_results: int = 10) -> dict:
    """Given a search query this tool searches
    for datasets from the SRA database and returns a dict.
    max_results determines the maximum results it will return.
    If unspecified by user, max_results is 10.
    No need to expand search beyond this.
    """
    df = client.search(query=query, detailed=False, max=max_results)
    return df.to_dict() if not df.empty else None


def fetch_publications(pmids: list[str]) -> list[dict]:
    """Fetches publication details for a list of PubMed IDs."""
    articles = []
    for pmid in pmids:
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            res = requests.get(url, timeout=10)
            if not res.ok:
                continue
            data = res.json()
            if data.get("result") and data["result"].get(str(pmid)):
                article_data = data["result"][str(pmid)]
                title = article_data.get("title", "")
                authors = article_data.get("authors", [])
                fulljournalname = article_data.get("fulljournalname", "")
                doi = ""
                for aid in article_data.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                        break
                articles.append(
                    {
                        "title": title,
                        "doi": f"https://doi.org/{doi}",
                        "authors": authors,
                        "fulljournalname": fulljournalname,
                    }
                )
            # NCBI recommends not more than 3 requests/sec
            time.sleep(0.34)
        except Exception:
            continue
    return articles


# entry point
def start_mcp_server():
    mcp.run(transport="stdio")

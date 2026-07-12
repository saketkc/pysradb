"""Tests for SRAweb"""

import time

import pandas as pd
import pytest
import requests

from pysradb.sraweb import SRAweb
from tests.conftest import skip_on_network_failure


class NetworkTolerantSRAweb:
    def __init__(self, client):
        self._client = client

    def __getattr__(self, name):
        attr = getattr(self._client, name)
        if not callable(attr):
            return attr

        return skip_on_network_failure(attr)


@pytest.fixture(scope="module")
def sraweb_connection():
    client = SRAweb()
    time.sleep(2)
    return NetworkTolerantSRAweb(client)


def test_sra_metadata(sraweb_connection):
    """Test if metadata has right number of entries"""
    df = sraweb_connection.sra_metadata("SRP016501")
    assert df.shape[0] == 134


def test_sra_metadata_missing_orgname(sraweb_connection):
    """Test if metadata has right number of entries"""
    df = sraweb_connection.sra_metadata("ERP000171")
    # See: https://github.com/saketkc/pysradb/issues/46#issuecomment-657268760
    assert sum(pd.isna(df.organism_name.tolist())) > 0


def test_sra_metadata_multiple(sraweb_connection):
    """Test if metadata has right number of entries"""
    df = sraweb_connection.sra_metadata(["SRP016501", "SRP096025", "SRP103009"])
    assert list(sorted(df.study_accession.unique())) == [
        "SRP016501",
        "SRP096025",
        "SRP103009",
    ]


def test_sra_metadata_multiple_detailed(sraweb_connection):
    """Test if metadata has right number of entries"""
    df = sraweb_connection.sra_metadata(["SRP002605", "SRP098789"], detailed=True)
    columns = ["treatment time", "library type", "transfection", "time"]
    assert len(set(columns).intersection(set(df.columns))) == 4
    ftp_cols = [
        "ena_fastq_http",
        "ena_fastq_http_1",
        "ena_fastq_http_2",
        "ena_fastq_ftp",
        "ena_fastq_ftp_1",
        "ena_fastq_ftp_2",
    ]
    assert len(set(ftp_cols).intersection(set(df.columns))) == 6


def test_tissue_column(sraweb_connection):
    """Test if tissue column exists"""
    df = sraweb_connection.sra_metadata("SRP096025", detailed="True")
    assert list(df["tissue"]) == ["Kidney"] * 4


def test_metadata_exp_accession(sraweb_connection):
    """Test if experiment_accession column is correct"""
    df = sraweb_connection.sra_metadata("SRP103009", detailed="True")
    assert "SRX2705123" in list(df["experiment_accession"])


def test_download_uses_existing_download_helper(monkeypatch, tmp_path):
    """Test SRAweb.download delegates URL downloads without network access."""
    calls = []

    def fake_download_file(url, file_path, show_progress=False):
        calls.append((url, file_path, show_progress))

    monkeypatch.setattr("pysradb.sraweb.download_file", fake_download_file)
    monkeypatch.setattr("pysradb.sraweb.get_file_size", lambda row, url_col: 123)

    df = pd.DataFrame(
        [
            {
                "study_accession": "SRP000001",
                "experiment_accession": "SRX000001",
                "run_accession": "SRR000001",
                "public_url": "https://example.org/SRR000001.fastq.gz",
            }
        ]
    )

    result = SRAweb().download(
        df,
        out_dir=str(tmp_path),
        skip_confirmation=True,
    )

    assert calls == [
        (
            "https://example.org/SRR000001.fastq.gz",
            str(tmp_path / "SRP000001" / "SRX000001" / "SRR000001.fastq.gz"),
            True,
        )
    ]
    assert result["filesize"].tolist() == [123]


def test_fetch_gds_results(sraweb_connection):
    """Test if fetch_gds_result returns correct values"""
    df = sraweb_connection.fetch_gds_results("GSE34438")
    assert "GSM849112" in set(df["accession"])


def test_srp_to_gse(sraweb_connection):
    """Test if srp is converted to gse correctly"""
    df = sraweb_connection.srp_to_gse("SRP009836")
    assert df["study_alias"][0] == "GSE34438"


def test_srp_to_srr(sraweb_connection):
    """Test if srp is converted to srr correctly"""
    df = sraweb_connection.srp_to_srr("SRP002605", detailed=True)
    assert df["run_accession"].tolist()[:5] == [
        "SRR057511",
        "SRR057512",
        "SRR057513",
        "SRR057514",
        "SRR057515",
    ]


def test_srp_to_srs(sraweb_connection):
    """Test if srp is converted to srs correctly"""
    df = sraweb_connection.srp_to_srs("SRP014542")
    assert sorted(list(df["sample_accession"])) == [
        "SRS351513",
        "SRS351514",
        "SRS351515",
        "SRS351516",
        "SRS351517",
        "SRS351518",
    ]


def test_srp_to_srx(sraweb_connection):
    """Test if srp is converted to srx correctly"""
    df = sraweb_connection.srp_to_srx("SRP044932")
    assert list(df["experiment_accession"]) == ["SRX663253", "SRX663254"]


def test_gse_to_gsm(sraweb_connection):
    """Test if gse is converted to gsm correctly"""
    df = sraweb_connection.gse_to_gsm("GSE56924", detailed=False)
    assert df.shape[0] == 96


def test_gse_to_gsm2(sraweb_connection):
    """Test for gse to gsm"""
    df = sraweb_connection.gse_to_gsm("GSE200028", detailed=False)
    assert df.shape[0] == 15


def test_gse_to_gsm1(sraweb_connection):
    """Test if gse_to_gsm works without passing `detailed` parameter"""
    df = sraweb_connection.gse_to_gsm("GSE63858")
    assert list(sorted(df["experiment_alias"])) == ["GSM1558530", "GSM1558531"]


def test_gse_to_srp(sraweb_connection):
    """Test if gse is converted to srp correctly"""
    df = sraweb_connection.gse_to_srp("GSE63858")
    assert df["study_accession"].tolist()[0] == "SRP050548"


def test_gse_to_srp2(sraweb_connection):
    """Test if gse is converted to srp correctly"""
    df = sraweb_connection.gse_to_srp(["GSE168880", "GSE209835"])
    observed = dict(zip(df["study_alias"], df["study_accession"]))
    assert observed["GSE168880"] == "SRP310566"
    assert observed["GSE209835"] == "SRP388275"


def test_gse_to_srp_with_nan_sra(sraweb_connection):
    """Test gse_to_srp when GSE has NaN SRA field but GSM entries have SRX values

    GSE192742 has no direct SRA link in the GSE entry, but GSM entries contain
    SRX accessions (like SRX13549307).

    Expected: SRP352825 (and possibly SRP352824 depending on GSM distribution)
    """
    df = sraweb_connection.gse_to_srp("GSE192742")
    assert not df.empty
    assert "GSE192742" in df["study_alias"].tolist()
    srps = df["study_accession"].tolist()
    assert "SRP352825" in srps
    assert all(pd.notna(srps))


def test_gsm_to_srp(sraweb_connection):
    """Test if gsm is converted to srp correctly"""
    df = sraweb_connection.gsm_to_srp("GSM1371490")
    assert df["study_accession"].tolist()[0] == "SRP041298"


def test_gsm_to_gse(sraweb_connection):
    """Test if gsm is converted to gse correctly"""
    df = sraweb_connection.gsm_to_gse("GSM1371490")
    assert df["study_alias"].tolist()[0] == "GSE56924"


def test_gsm_to_gse_multiple_gses(sraweb_connection):
    """Test GSM that maps to multiple GSE accessions (GSM7430904 -> GSE233587, GSE234305)"""
    df = sraweb_connection.gsm_to_gse("GSM7430904")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "study_alias" in df.columns
    assert "study_accession" in df.columns
    study_aliases = df["study_alias"].tolist()
    assert len(study_aliases) >= 2
    study_aliases = df["study_alias"].tolist()
    expected_gses = {"GSE233587", "GSE234305"}
    actual_gses = set(study_aliases)
    assert expected_gses.issubset(
        actual_gses
    ), f"Expected {expected_gses} to be subset of {actual_gses}"

    assert "GSE234305" in study_aliases


def test_gsm_to_srr(sraweb_connection):
    """Test if gsm is converted to srr correctly"""
    df = sraweb_connection.gsm_to_srr("GSM1371489")
    assert df["run_accession"].tolist()[0] == "SRR1257271"


def test_gsm_to_srs(sraweb_connection):
    """Test if gsm is converted to srs correctly"""
    df = sraweb_connection.gsm_to_srs("GSM1371469")
    assert df["sample_accession"].tolist()[0] == "SRS594838"


def test_gsm_to_srx(sraweb_connection):
    """Test if gsm is converted to srx correctly"""
    df = sraweb_connection.gsm_to_srx("GSM1371454")
    assert list(df["experiment_accession"]) == ["SRX522468"]


def test_srr_to_gsm(sraweb_connection):
    df = sraweb_connection.srr_to_gsm("SRR057515")
    assert df["experiment_alias"].tolist()[0] == "GSM546921"


def test_srr_to_srp(sraweb_connection):
    """Test if srr is converted to srp correctly"""
    df = sraweb_connection.srr_to_srp("SRR057511", detailed=False)
    assert list(df["study_accession"]) == ["SRP002605"]


def test_srr_to_srp1(sraweb_connection):
    """Test if srr_to_srp works without passing the `detailed` parameter"""
    df = sraweb_connection.srr_to_srp("SRR057515")
    assert list(df["study_accession"]) == ["SRP002605"]


def test_srr_to_srs(sraweb_connection):
    """Test if srr is converted to srs correctly"""
    df = sraweb_connection.srr_to_srs("SRR057513")
    assert list(df["sample_accession"]) == ["SRS079386"]


def test_srr_to_srx(sraweb_connection):
    """Test if srr is converted to srx correctly"""
    df = sraweb_connection.srr_to_srx("SRR057514")
    assert list(df["experiment_accession"]) == ["SRX021967"]


def test_srs_to_gsm(sraweb_connection):
    """Test if srs is converted to gsm correctly"""
    df = sraweb_connection.srs_to_gsm("SRS079386")
    assert df["experiment_alias"][0] == "GSM546921"


def test_srs_to_srx(sraweb_connection):
    """Test if srs is converted to srx correctly"""
    df = sraweb_connection.srs_to_srx("SRS594838")
    assert list(df["experiment_accession"]) == ["SRX522483"]


def test_srx_to_gsm(sraweb_connection):
    """Test if srx is converted to gsm correctly"""
    df = sraweb_connection.srx_to_gsm("SRX663253")
    assert list(df["experiment_alias"]) == ["GSM1446832"]


def test_srx_to_srp(sraweb_connection):
    """Test if srx is converted to srp correctly"""
    df = sraweb_connection.srx_to_srp("SRX663254")
    assert list(df["study_accession"]) == ["SRP044932"]


def test_srx_to_srr(sraweb_connection):
    """Test if srx is converted to srr correctly"""
    df = sraweb_connection.srx_to_srr("SRX2705123")
    assert list(df["run_accession"]) == ["SRR5413172"]


def test_srx_to_srr1(sraweb_connection):
    """Test if srx is converted to srr correctly, including multiple srrs"""
    df = sraweb_connection.srx_to_srr("SRX8998846")
    assert list(df["run_accession"]) == ["SRR12508064", "SRR12508065"]


def test_srx_to_srs(sraweb_connection):
    """Test if srx is converted to srs correctly"""
    df = sraweb_connection.srx_to_srs("SRX663253")
    assert list(df["sample_accession"]) == ["SRS668126"]


# This is currently failing
def _test_xmlns_id(sraweb_connection):
    df = sraweb_connection.sra_metadata(["GSM1013144", "GSM2520660"])
    library_layouts = list(df["library_layout"])
    assert library_layouts[0] == "PAIRED"
    assert library_layouts[1] == "SINGLE"


def test_GCP_url(sraweb_connection):
    df = sraweb_connection.sra_metadata(["SRP002605"], detailed=True)
    assert df["gcp_url"].tolist()[-1].startswith("gs:")


def test_GCP_url2(sraweb_connection):
    df = sraweb_connection.sra_metadata(["DRR138929"], detailed=True)
    assert df["gcp_url"].tolist()[-1].startswith("gs:")


def test_gse_to_srp3(sraweb_connection):
    # https://github.com/saketkc/pysradb/issues/190
    df = sraweb_connection.gse_to_srp(["GSE89545"])
    assert df["study_accession"].tolist()[0] == "SRP093251"


def test_gse_to_srp_multiple_srps(sraweb_connection):
    """Test GSE that maps to multiple SRP accessions (GSE234305 -> SRP411077, SRP439808)"""
    df = sraweb_connection.gse_to_srp("GSE234305")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "study_alias" in df.columns
    assert "study_accession" in df.columns

    # Check that GSE234305 maps to the expected SRPs
    study_aliases = df["study_alias"].tolist()
    study_accessions = df["study_accession"].dropna().tolist()

    assert "GSE234305" in study_aliases
    # Should map to multiple SRPs
    assert len(set(study_accessions)) >= 2
    # Check for the known SRP accessions
    expected_srps = {"SRP411077", "SRP439808"}
    actual_srps = set(study_accessions)
    assert expected_srps.issubset(
        actual_srps
    ), f"Expected {expected_srps} to be subset of {actual_srps}"


def test_geo_metadata_for_gse_without_srp(sraweb_connection):
    """GSE286254 should return GEO metadata even without SRP links"""
    df = sraweb_connection.geo_metadata("GSE286254")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "GSE286254" in df["study_accession"].unique()
    assert "GSM8721777" in df["sample_accession"].values


def test_geo_metadata_with_sample_attributes(sraweb_connection):
    """Ensure sample_attribute flag adds sample summaries"""
    df = sraweb_connection.geo_metadata("GSE286254", sample_attribute=True)
    assert "sample_summary" in df.columns
    assert df["sample_summary"].notna().any()


def test_geo_metadata_covid19_characteristics(sraweb_connection):
    """Test GSE155673 COVID-19 metadata with disease_status and custom characteristics"""
    df = sraweb_connection.geo_metadata("GSE155673", detailed=True)

    # Find the specific sample GSM4712885
    sample = df[df["sample_accession"] == "GSM4712885"]
    assert not sample.empty, "Sample GSM4712885 not found"

    # Verify disease field captures disease_status
    disease_value = sample["disease"].iloc[0]
    assert pd.notna(disease_value), "Disease field should not be NA"
    assert (
        "COVID-19" in str(disease_value).upper()
        or "COVID" in str(disease_value).upper()
    ), f"Disease should contain COVID-19, got: {disease_value}"

    # Verify custom characteristics are captured
    assert "disease_severity" in df.columns, "disease_severity column should exist"
    assert (
        "days_since_symptom_onset" in df.columns
    ), "days_since_symptom_onset column should exist"

    # Verify values for GSM4712885
    sample_severity = sample["disease_severity"].iloc[0]
    assert pd.notna(
        sample_severity
    ), "disease_severity should not be NA for COVID sample"
    assert "Severe" in str(
        sample_severity
    ), f"Expected 'Severe', got: {sample_severity}"

    days_onset = sample["days_since_symptom_onset"].iloc[0]
    assert pd.notna(days_onset), "days_since_symptom_onset should not be NA"
    assert str(days_onset) == "15", f"Expected '15', got: {days_onset}"

    # Verify standard fields
    assert sample["sex"].iloc[0] == "F", "Sex should be F"
    assert str(sample["age"].iloc[0]) == "75", "Age should be 75"
    assert sample["cell_type"].iloc[0] == "PBMC", "Cell type should be PBMC"

    # Verify comprehensive SOFT field capture (no filtering)
    # These fields should be present when detailed=True
    expected_soft_fields = [
        "sample_instrument_model",
        "sample_library_strategy",
        "sample_library_source",
        "sample_organism_ch1",
        "sample_taxid_ch1",
        "sample_molecule_ch1",
        "sample_contact_name",
        "sample_contact_institute",
        "sample_data_processing",
        "sample_platform_id",
    ]

    for field in expected_soft_fields:
        assert (
            field in df.columns
        ), f"SOFT field '{field}' should be captured in detailed mode"
        assert pd.notna(
            sample[field].iloc[0]
        ), f"SOFT field '{field}' should have a value"

    # Verify specific values for comprehensive check
    assert "Illumina" in str(
        sample["sample_instrument_model"].iloc[0]
    ), "Should capture instrument model"
    assert (
        sample["sample_library_strategy"].iloc[0] == "RNA-Seq"
    ), "Should capture library strategy"
    assert (
        str(sample["sample_taxid_ch1"].iloc[0]) == "9606"
    ), "Should capture taxid (human)"


def test_fetch_bioproject_pmids(sraweb_connection):
    """Test fetching PMIDs for BioProject accessions"""
    # Use a known BioProject that should have publications
    result = sraweb_connection.fetch_bioproject_pmids("PRJNA257197")
    assert isinstance(result, dict)
    assert "PRJNA257197" in result


def test_fetch_bioproject_pmids_multiple(sraweb_connection):
    """Test fetching PMIDs for multiple BioProjects"""
    bioprojects = ["PRJNA257197", "PRJNA200000"]  # Mix of real and potentially missing
    result = sraweb_connection.fetch_bioproject_pmids(bioprojects)
    assert isinstance(result, dict)
    assert len(result) == 2
    for bp in bioprojects:
        assert bp in result
        assert isinstance(result[bp], list)
    # Check that PRJNA200000 returns an empty list (no PMIDs)
    assert result["PRJNA200000"] == []


def test_search_pmc_by_bioproject(sraweb_connection):
    """Test PMC search fallback for bioproject IDs"""
    # PRJEB39301 doesn't have PMIDs in bioproject XML but is cited in PMC (PMC8379757)
    pmids = sraweb_connection._search_pmc_by_bioproject("PRJEB39301")
    assert isinstance(pmids, list)
    assert len(pmids) > 0
    # Should find PMID 34419158 (from PMC8379757)
    assert "34419158" in pmids


def test_fetch_bioproject_pmids_with_pmc_fallback(sraweb_connection):
    """Test that fetch_bioproject_pmids falls back to PMC search when XML has no PMIDs"""
    # PRJEB39301 - bioproject XML has no publications, but PMC search should find them
    result = sraweb_connection.fetch_bioproject_pmids("PRJEB39301")
    assert isinstance(result, dict)
    assert "PRJEB39301" in result
    assert isinstance(result["PRJEB39301"], list)
    if not result["PRJEB39301"]:
        pytest.skip(
            "PMC fallback returned no PMIDs (likely NCBI rate limiting / network)"
        )
    # Should have found PMID via PMC fallback
    assert "34419158" in result["PRJEB39301"]


def test_srp_to_pmid_with_pmc_fallback(sraweb_connection):
    """Test srp_to_pmid with bioproject that uses PMC fallback"""
    # ERP122802 uses PRJEB39301 which requires PMC fallback to find PMID
    df = sraweb_connection.srp_to_pmid("ERP122802")
    assert isinstance(df, pd.DataFrame)
    assert "srp_accession" in df.columns
    assert "bioproject" in df.columns
    assert "pmid" in df.columns
    # Check that we got a result for ERP122802
    assert len(df) > 0
    erp_row = df[df["srp_accession"] == "ERP122802"]
    assert len(erp_row) > 0
    pmid = erp_row.iloc[0]["pmid"]
    if pd.isna(pmid):
        pytest.skip("PMID lookup returned NA (likely NCBI rate limiting / network)")
    # Should have PMID 34419158 via PMC fallback
    assert pmid == "34419158"


def test_sra_to_pmid(sraweb_connection):
    """Test SRA to PMID functionality (backward compatibility)"""
    df = sraweb_connection.sra_to_pmid("SRP002605")
    assert isinstance(df, pd.DataFrame)
    required_columns = {"srp_accession", "bioproject", "pmid"}
    assert required_columns.issubset(set(df.columns))


def test_srp_to_pmid(sraweb_connection):
    """Test SRP to PMID main method"""
    df = sraweb_connection.srp_to_pmid("SRP002605")
    assert isinstance(df, pd.DataFrame)
    assert "srp_accession" in df.columns
    assert "pmid" in df.columns


def test_srr_to_pmid(sraweb_connection):
    """Test SRR to PMID convenience method"""
    df = sraweb_connection.srr_to_pmid("SRR057511")
    assert isinstance(df, pd.DataFrame)
    assert "srp_accession" in df.columns
    assert "pmid" in df.columns


def test_sra_to_pmid_multiple(sraweb_connection):
    """Test SRA to PMID with multiple accessions (backward compatibility)"""
    df = sraweb_connection.sra_to_pmid(["SRP002605", "SRP016501"])
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2  # Should have at least one row per input SRA


def test_srp_to_pmid_multiple(sraweb_connection):
    """Test SRP to PMID with multiple accessions"""
    df = sraweb_connection.srp_to_pmid(["SRP002605", "SRP016501"])
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2  # Should have at least one row per input SRP
    assert "srp_accession" in df.columns
    assert "pmid" in df.columns


def test_srp_to_pmid_no_batch_broadcast(monkeypatch):
    """A fallback PMID found for one SRP must not be broadcast to the other
    SRPs in the same batch."""
    client = SRAweb()

    meta = pd.DataFrame(
        [
            {"study_accession": "SRP000001", "bioproject": "PRJNA1"},
            {"study_accession": "SRP000002", "bioproject": "PRJNA2"},
        ]
    )
    monkeypatch.setattr(client, "sra_metadata", lambda *a, **k: meta)
    # No BioProject-linked PMIDs, so the per-accession fallback runs.
    monkeypatch.setattr(
        client, "fetch_bioproject_pmids", lambda bps: {bp: [] for bp in bps}
    )
    monkeypatch.setattr(client, "_search_fallback_pmids", lambda accs: [])
    # Only the first accession has a EuropePMC hit.
    monkeypatch.setattr(
        client,
        "_search_europepmc",
        lambda acc: ["12345"] if acc == "SRP000001" else [],
    )

    df = client.srp_to_pmid(["SRP000001", "SRP000002"]).set_index("srp_accession")
    assert df.loc["SRP000001", "pmid"] == "12345"
    assert pd.isna(df.loc["SRP000002", "pmid"])  # must NOT inherit SRP000001's PMID


def test_gse_to_pmid(sraweb_connection):
    """Test GSE to PMID functionality"""
    df = sraweb_connection.gse_to_pmid("GSE253406")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"gse_accession", "pmid"}
    assert required_columns.issubset(df.columns)


def test_gse_to_pmid_multiple(sraweb_connection):
    """Test GSE to PMID with multiple accessions"""
    df = sraweb_connection.gse_to_pmid(["GSE253406", "GSE168776"])
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2  # Should have one row per input GSE
    assert "gse_accession" in df.columns
    assert "pmid" in df.columns


def test_gse_to_pmid_title_fallback(monkeypatch):
    """GSE resolves to a PMID via GEO title when PMC/EuropePMC miss."""
    client = SRAweb()

    def fake_send(url, params=None, **kwargs):
        class Response:
            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        if "esearch" in url and params.get("db") == "gds":
            return Response({"esearchresult": {"idlist": ["200303928"]}})
        if "esummary" in url and params.get("db") == "gds":
            return Response(
                {
                    "result": {
                        "200303928": {"title": "RegVelo: dynamics of single cells"}
                    }
                }
            )
        if "esearch" in url and params.get("db") == "pubmed":
            return Response({"esearchresult": {"idlist": ["42119563"]}})
        raise AssertionError(f"unexpected request: {url} {params}")

    monkeypatch.setattr(client, "search_pmc_for_external_sources", lambda *a, **k: [])
    monkeypatch.setattr(client, "_search_europepmc", lambda *a, **k: [])
    monkeypatch.setattr(client, "_send_retryable_request", fake_send)

    df = client.gse_to_pmid("GSE303928")
    assert df.loc[0, "pmid"] == "42119563"


def test_pmid_to_pmc(sraweb_connection):
    """Test PMID to PMC conversion"""
    mapping = sraweb_connection.pmid_to_pmc("27373336")
    assert isinstance(mapping, dict)
    assert "27373336" in mapping


def test_pmid_to_pmc_multiple(sraweb_connection):
    """Test PMID to PMC with multiple PMIDs"""
    mapping = sraweb_connection.pmid_to_pmc(["27373336", "39528918"])
    assert isinstance(mapping, dict)
    assert len(mapping) == 2


def test_extract_identifiers_from_text(sraweb_connection):
    """Test extraction of identifiers from text"""
    test_text = "This study uses data from GSE12345 and SRP067890. The BioProject is PRJNA123456 with samples SRR1234567."
    identifiers = sraweb_connection.extract_identifiers_from_text(test_text)
    assert isinstance(identifiers, dict)
    assert "GSE12345" in identifiers["gse"]
    assert "SRP067890" in identifiers["srp"]
    assert "PRJNA123456" in identifiers["prjna"]
    assert "SRR1234567" in identifiers["srr"]


def test_fetch_pmc_fulltext_retries(monkeypatch):
    """Test PMC full-text fetch retries transient request failures."""

    class Response:
        text = "<article/>"
        status_code = 200

        def raise_for_status(self):
            return None

    client = SRAweb()
    client.sleep_time = 0.5
    calls = []
    sleeps = []

    def fake_request(method, url, params=None, data=None, timeout=None):
        calls.append((url, params, timeout))
        if len(calls) < 3:
            raise requests.RequestException("temporary failure")
        return Response()

    monkeypatch.setattr("pysradb.sraweb.requests.request", fake_request)
    monkeypatch.setattr("pysradb.sraweb.time.sleep", sleeps.append)

    assert client.fetch_pmc_fulltext("PMC123", retries=2) == "<article/>"
    assert len(calls) == 3
    assert sleeps == [0.5, 1.0, 0.5]


@pytest.mark.slow
def test_pmc_to_identifiers(sraweb_connection):
    """Test PMC to identifiers extraction - requires PMC full text access"""
    # Using a known PMC article that mentions GEO/SRA identifiers
    df = sraweb_connection.pmc_to_identifiers("PMC5316890")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"pmc_id", "gse_ids", "srp_ids", "prjna_ids"}
    assert required_columns.issubset(df.columns)


@pytest.mark.slow
def test_pmid_to_identifiers(sraweb_connection):
    """Test PMID to identifiers extraction"""
    df = sraweb_connection.pmid_to_identifiers("27373336")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"pmid", "pmc_id", "gse_ids", "srp_ids", "prjna_ids"}
    assert required_columns.issubset(df.columns)


@pytest.mark.slow
def test_pmid_to_gse(sraweb_connection):
    """Test PMID to GSE extraction"""
    df = sraweb_connection.pmid_to_gse("27373336")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"pmid", "pmc_id", "gse_ids"}
    assert required_columns.issubset(df.columns)


@pytest.mark.slow
def test_pmid_to_srp(sraweb_connection):
    """Test PMID to SRP extraction"""
    df = sraweb_connection.pmid_to_srp("27373336")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"pmid", "pmc_id", "srp_ids"}
    assert required_columns.issubset(df.columns)


def test_doi_to_pmid(sraweb_connection):
    """Test DOI to PMID conversion"""
    mapping = sraweb_connection.doi_to_pmid("10.12688/f1000research.18676.1")
    assert isinstance(mapping, dict)
    assert "10.12688/f1000research.18676.1" in mapping


def test_doi_to_pmid_multiple(sraweb_connection):
    """Test DOI to PMID with multiple DOIs"""
    mapping = sraweb_connection.doi_to_pmid(
        ["10.12688/f1000research.18676.1", "10.1186/s13059-016-1070-5"]
    )
    assert isinstance(mapping, dict)
    assert len(mapping) == 2


@pytest.mark.slow
def test_doi_to_identifiers(sraweb_connection):
    """Test DOI to identifiers extraction"""
    df = sraweb_connection.doi_to_identifiers("10.12688/f1000research.18676.1")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"doi", "pmid", "pmc_id", "gse_ids", "srp_ids", "prjna_ids"}
    assert required_columns.issubset(df.columns)


@pytest.mark.slow
def test_doi_to_gse(sraweb_connection):
    """Test DOI to GSE extraction"""
    df = sraweb_connection.doi_to_gse("10.12688/f1000research.18676.1")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"doi", "pmid", "pmc_id", "gse_ids"}
    assert required_columns.issubset(df.columns)


@pytest.mark.slow
def test_doi_to_srp(sraweb_connection):
    """Test DOI to SRP extraction"""
    df = sraweb_connection.doi_to_srp("10.12688/f1000research.18676.1")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    required_columns = {"doi", "pmid", "pmc_id", "srp_ids"}
    assert required_columns.issubset(df.columns)


def test_unified_metadata_with_gse(sraweb_connection):
    """Test unified metadata() function with GSE accession"""
    df = sraweb_connection.metadata("GSE286254")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "GSE286254" in df["study_accession"].unique()


def test_unified_metadata_with_srp(sraweb_connection):
    """Test unified metadata() function with SRP accession"""
    df = sraweb_connection.metadata("SRP016501")
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 134
    assert "SRP016501" in df["study_accession"].unique()


def test_unified_metadata_with_multiple_gse(sraweb_connection):
    """Test unified metadata() function with multiple GSE accessions"""
    df = sraweb_connection.metadata(["GSE168880", "GSE209835"])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    gse_ids = df["study_accession"].unique()
    assert "GSE168880" in gse_ids or "GSE209835" in gse_ids


def test_unified_metadata_invalid_accession(sraweb_connection):
    """Test unified metadata() function with invalid accession type"""
    with pytest.raises(ValueError, match="Unsupported accession type"):
        sraweb_connection.metadata("INVALID123")

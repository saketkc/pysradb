"""Tests for SRAweb"""

import time

import pandas as pd
import pytest

from pysradb.sraweb import SRAweb


@pytest.fixture(scope="module")
def sraweb_connection():
    db = SRAweb()
    time.sleep(2)
    return db


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


def test_fetch_gds_results(sraweb_connection):
    """Test if fetch_gds_result returns correct values"""
    df = sraweb_connection.fetch_gds_results("GSE34438")
    assert df["accession"][1] == "GSM849112"


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
    assert df["study_accession"].tolist()[0] == "SRP310566"
    assert df["study_accession"].tolist()[1] == "SRP388275"


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
    study_accessions = df["study_accession"].tolist()

    assert "GSE234305" in study_aliases
    # Should map to multiple SRPs
    assert len(set(study_accessions)) >= 2
    # Check for the known SRP accessions
    expected_srps = {"SRP411077", "SRP439808"}
    actual_srps = set(study_accessions)
    assert expected_srps.issubset(
        actual_srps
    ), f"Expected {expected_srps} to be subset of {actual_srps}"


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

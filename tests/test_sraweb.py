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
    df = sraweb_connection.srp_to_srr("SRP002605")
    assert sorted(list(df["run_accession"]))[:5] == [
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
    assert list(df["experiment_accession"]) == [
        "SRX663254",
        "SRX663253",
    ]


def test_gse_to_gsm(sraweb_connection):
    """Test if gse is converted to gsm correctly"""
    df = sraweb_connection.gse_to_gsm("GSE56924", detailed=False)
    assert df.shape[0] == 96


def test_gse_to_gsm1(sraweb_connection):
    """Test if gse_to_gsm works without passing `detailed` parameter"""
    df = sraweb_connection.gse_to_gsm("GSE63858")
    assert list(sorted(df["experiment_alias"])) == ["GSM1558530", "GSM1558531"]


def test_gse_to_srp(sraweb_connection):
    """Test if gse is converted to srp correctly"""
    df = sraweb_connection.gse_to_srp("GSE63858")
    assert df["study_accession"][0] == "SRP050548"


def test_gsm_to_srp(sraweb_connection):
    """Test if gsm is converted to srp correctly"""
    df = sraweb_connection.gsm_to_srp("GSM1371490")
    assert df["study_accession"][0] == "SRP041298"


def test_gsm_to_gse(sraweb_connection):
    """Test if gsm is converted to gse correctly"""
    df = sraweb_connection.gsm_to_gse("GSM1371490")
    assert df["study_alias"][0] == "GSE56924"


def test_gsm_to_srr(sraweb_connection):
    """Test if gsm is converted to srr correctly"""
    df = sraweb_connection.gsm_to_srr("GSM1371489")
    assert df["run_accession"][0] == "SRR1257271"


def test_gsm_to_srs(sraweb_connection):
    """Test if gsm is converted to srs correctly"""
    df = sraweb_connection.gsm_to_srs("GSM1371469")
    assert df["sample_accession"][0] == "SRS594838"


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
    assert list(df["study_accession"]) == ["SRP002605"] * 2


def test_srr_to_srp1(sraweb_connection):
    """Test if srr_to_srp works without passing the `detailed` parameter"""
    df = sraweb_connection.srr_to_srp("SRR057515")
    assert list(df["study_accession"]) == ["SRP002605"] * 3


def test_srr_to_srs(sraweb_connection):
    """Test if srr is converted to srs correctly"""
    df = sraweb_connection.srr_to_srs("SRR057513")
    assert list(df["sample_accession"]) == ["SRS079386"] * 3


def test_srr_to_srx(sraweb_connection):
    """Test if srr is converted to srx correctly"""
    df = sraweb_connection.srr_to_srx("SRR057514")
    assert list(df["experiment_accession"]) == ["SRX021967"] * 3


def test_srs_to_gsm(sraweb_connection):
    """Test if srs is converted to gsm correctly"""
    df = sraweb_connection.srs_to_gsm("SRS079386")
    assert list(df["experiment_alias"]) == ["GSM546921"] * 3


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


def test_srx_to_srs(sraweb_connection):
    """Test if srx is converted to srs correctly"""
    df = sraweb_connection.srx_to_srs("SRX663253")
    assert list(df["sample_accession"]) == ["SRS668126"]


def test_xmlns_id(sraweb_connection):
    df = sraweb_connection.sra_metadata(["GSM1013144", "GSM2520660"])
    assert list(df["library_layout"]) == ["PAIRED", "SINGLE"]

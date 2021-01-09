"""Tests for sradb.py
"""

import os
from sqlite3 import OperationalError

import pytest

from pysradb import SRAdb
from pysradb.filter_attrs import guess_cell_type
from pysradb.filter_attrs import guess_strain_type
from pysradb.filter_attrs import guess_tissue_type


@pytest.fixture(scope="module")
def sradb_connection(conf_download_sradb_file):
    db_file = conf_download_sradb_file
    db = SRAdb(db_file)
    return db


def test_list_tables(sradb_connection):
    sra_tables = sradb_connection.list_tables()
    assert sra_tables == [
        "metaInfo",
        "submission",
        "study",
        "sample",
        "experiment",
        "run",
        "sra",
        "sra_ft",
        "sra_ft_content",
        "sra_ft_segments",
        "sra_ft_segdir",
        "col_desc",
        "fastq",
    ]


def test_list_fields(sradb_connection):
    fields = sradb_connection.list_fields("study")
    assert fields == [
        "study_ID",
        "study_alias",
        "study_accession",
        "study_title",
        "study_type",
        "study_abstract",
        "broker_name",
        "center_name",
        "center_project_name",
        "study_description",
        "related_studies",
        "primary_study",
        "sra_link",
        "study_url_link",
        "xref_link",
        "study_entrez_link",
        "ddbj_link",
        "ena_link",
        "study_attribute",
        "submission_accession",
        "sradb_updated",
    ]


def test_desc_table(sradb_connection):
    names = sorted(sradb_connection.desc_table("sra_ft").name.tolist())
    assert names[:7] == [
        "SRR_bamFile",
        "SRX_bamFile",
        "SRX_fastqFTP",
        "adapter_spec",
        "anonymized_name",
        "base_caller",
        "bases",
    ]


def test_all_row_counts(sradb_connection):
    assert sradb_connection.all_row_counts().loc["metaInfo", "count"] == 2


def test_all_row_counts2(sradb_connection):
    assert len(sradb_connection.all_row_counts()) == 13


def test_sra_metadata(sradb_connection):
    df = sradb_connection.sra_metadata("SRP017942")
    assert df["experiment_accession"][0] == "SRX217027"


def test_sra_metadata2(sradb_connection):
    df = sradb_connection.sra_metadata(
        "SRP017942", detailed=True, expand_sample_attributes=True
    )
    assert "3xflag-gfp" in df["transfected_with"].tolist()


def test_search(sradb_connection):
    df = sradb_connection.search_sra(search_str="breast cancer")
    assert len(df.index)


def test_search2(sradb_connection):
    df = sradb_connection.search_sra(
        '"salivary microbiome" AND "diabetes mellitus"', detailed=True
    )
    assert "SRP241848" in df["study_accession"].to_list()


def test_search_by_expt_id(sradb_connection):
    df = sradb_connection.search_by_expt_id("SRX1254413")
    assert df.study_name.tolist()[0] == "GSE73136"


def test_search_by_expt_id2(sradb_connection):
    srx_id = "SRX116363"
    df_expt = sradb_connection.search_by_expt_id(srx_id)
    sra_id = df_expt["submission_accession"].loc[0]
    df = sradb_connection.sra_metadata(sra_id)
    connected_srp = sradb_connection.srx_to_srp("SRX116363").iloc[0, 1]
    assert (srx_id in df["experiment_accession"].to_list()) and (
        connected_srp == "SRP010374"
    )


# def test_download_fasp(sradb_connection):
#    df = sradb_connection.sra_metadata("SRP098789")
#    df = df[df.experiment_accession == "SRX2536403"]
#    sradb_connection.download(df=df, out_dir="data/", skip_confirmation=True)
#    assert os.path.isfile("data/SRP098789/SRX2536403/SRR5227288.sra")
#    assert os.path.getsize("data/SRP098789/SRX2536403/SRR5227288.sra")
#    os.remove("data/SRP098789/SRX2536403/SRR5227288.sra")


@pytest.mark.xfail
def test_download_ftp(sradb_connection):
    # This happens to fail because of ftp problems
    df = sradb_connection.sra_metadata("SRP098789")
    df = df[df.experiment_accession == "SRX2536404"]
    sradb_connection.download(
        df=df, protocol="ftp", out_dir="data/", skip_confirmation=True
    )
    assert os.path.isfile("data/SRP098789/SRX2536404/SRR5227289.sra")
    assert os.path.getsize("data/SRP098789/SRX2536404/SRR5227289.sra")
    os.remove("data/SRP098789/SRX2536404/SRR5227289.sra")


def test_tissue_type(sradb_connection):
    df = sradb_connection.sra_metadata("SRP016501", detailed=True)
    df = df[df.experiment_accession == "SRX196389"]
    cell_type = df["sample_attribute"].apply(lambda x: guess_cell_type(x))
    tissue_type = df["sample_attribute"].apply(lambda x: guess_tissue_type(x))
    assert cell_type.tolist() == ["chicken_brain"]
    assert tissue_type.tolist() == ["brain"]


def test_strain_type(sradb_connection):
    df = sradb_connection.sra_metadata("SRP043036", detailed=True)
    df = df.sort_values(by="experiment_accession")
    strains = df["sample_attribute"].apply(lambda x: guess_strain_type(x)).tolist()
    assert strains == [
        "by4741",
        "by4741",
        "by4741",
        "by4741",
        "by4741",
        "by4741",
        "by4741",
        "by4741",
        "s288c",
        "s288c",
        "s288c",
        "s288c",
    ]


def test_srp_to_srx(sradb_connection):
    assert len(sradb_connection.srp_to_srx("SRP082570")) == 14


def test_srp_to_srr(sradb_connection):
    df = sradb_connection.srp_to_srr("SRP091987")
    assert sorted(list(df["run_accession"])[:3]) == [
        "SRR4447104",
        "SRR4447105",
        "SRR4447106",
    ]


def test_srp_to_gse(sradb_connection):
    gse_id = sradb_connection.srp_to_gse("SRP050443").iloc[0, 1]
    df = sradb_connection.gse_to_gsm(gse_id)
    assert "GSM1557451" in df["experiment_alias"].to_list()


def test_gsm_to_gse(sradb_connection):
    df = sradb_connection.gsm_to_gse(["GSM1020651", "GSM1020664", "GSM1020771"])
    assert set(list(df["study_alias"])) == {"GSE41637"}


def test_srs_to_gsm(sradb_connection):
    df = sradb_connection.srs_to_gsm("SRS1757470")
    assert "GSM2358940" == df.iloc[0, 1]


@pytest.mark.xfail(raises=ValueError)
def test_wrong_input_metadata(sradb_connection):
    df = sradb_connection.sra_metadata("should_throw_error")

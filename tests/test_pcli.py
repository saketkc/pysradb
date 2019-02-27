"""Tests for cli.py
"""

import os
from pysradb import SRAdb

import pytest
import subprocess


@pytest.fixture(scope="module")
def sradb_connection(conf_download_sradb_file):
    db_file = conf_download_sradb_file
    db = SRAdb(db_file)
    return db


def test_all_row_counts_sra(sradb_connection):
    assert sradb_connection.all_row_counts().loc["metaInfo", "count"] == 2


def test_download():
    result = subprocess.run(
        [
            "pysradb",
            "download",
            "-y",
            "--db",
            "data/SRAmetadb.sqlite",
            "--out-dir",
            "srp_downloads",
            "-p",
            "SRP063852",
        ]
    )
    assert "SRP063852" in result.output
    assert os.path.getsize("srp_downloads/SRP063852/SRX1254413/SRR2433794.sra")


def test_sra_metadata():
    result = subprocess.run(
        ["pysradb", "metadata", "SRP098789", "--db", "data/SRAmetadb.sqlite"]
    )
    assert "SRX2536403" in result.output


def test_sra_metadata():
    result = subprocess.run(
        [
            "pysradb",
            "metadata",
            "SRP098789",
            "--db",
            "data/SRAmetadb.sqlite",
            "--detailed",
            "--expand",
        ]
    )
    assert "treatment_time" in result.output


def test_srp_to_srx():
    result = subprocess.run(
        ["pysradb", "srp-to-srx", "SRP098789", "--db", "data/SRAmetadb.sqlite"]
    )
    assert "SRX2536403" in result.output


def test_srp_assay():
    result = subprocess.run(
        ["pysradb", "metadata", "SRP098789", "--db", "data/SRAmetadb.sqlite", "--assay"]
    )
    assert "RNA-Seq" in result.output


def srr_to_srx():
    result = subprocess.run(
        [
            "pysradb",
            "srr-to-srx",
            "--db",
            "data/SRAmetadb.sqlite",
            "SRR5227288",
            "SRR649752",
            "--desc",
        ]
    )
    assert "3T3 cells" in result.output


def srx_to_srr():
    result = subprocess.run(
        [
            "pysradb",
            "srr-to-srx",
            "--db",
            "data/SRAmetadb.sqlite",
            "SRX217956",
            "SRX2536403",
            "--desc",
        ]
    )
    assert "3T3 cells" in result.output

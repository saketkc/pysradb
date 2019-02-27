"""Tests for cli.py
"""

import os
from pysradb import SRAdb

import pytest
from shlex import quote
from shlex import split
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
        ],
        capture_output=True,
    )
    assert "SRP063852" in str(result.stdout)
    assert os.path.getsize("srp_downloads/SRP063852/SRX1254413/SRR2433794.sra")


def test_sra_metadata():
    result = subprocess.run(
        ["pysradb", "metadata", "SRP098789", "--db", "data/SRAmetadb.sqlite"],
        capture_output=True,
    )
    assert "SRX2536403" in str(result.stdout)


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
        ],
        capture_output=True,
    )
    assert "treatment_time" in str(result.stdout)


def test_srp_to_srx():
    result = subprocess.run(
        ["pysradb", "srp-to-srx", "SRP098789", "--db", "data/SRAmetadb.sqlite"],
        capture_output=True,
    )
    assert "SRX2536403" in str(result.stdout)


def test_srp_assay():
    result = subprocess.run(
        [
            "pysradb",
            "metadata",
            "SRP098789",
            "--db",
            "data/SRAmetadb.sqlite",
            "--assay",
        ],
        capture_output=True,
    )
    assert "RNA-Seq" in str(result.stdout)


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
        ],
        capture_output=True,
    )
    assert "3T3 cells" in str(result.stdout)


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
        ],
        capture_output=True,
    )
    assert "3T3 cells" in str(result.stdout)


def test_sra_metadata_detail():
    result = subprocess.run(
        split(
            "pysradb metadata --db data/SRAmetadb.sqlite SRP075720 --detailed --expand"
        ),
        capture_output=True,
    )
    assert "retina" in str(result.stdout)


def test_srp_to_gse():
    result = subprocess.run(
        split("pysradb srp-to-gse --db data/SRAmetadb.sqlite SRP075720"),
        capture_output=True,
    )
    assert "GSE81903" in str(result.stdout)


def test_gsm_to_srp():
    result = subprocess.run(
        split("pysradb gsm-to-srp --db data/SRAmetadb.sqlite GSM2177186"),
        capture_output=True,
    )
    assert "SRP075720" in str(result.stdout)


def test_gsm_to_gse():
    result = subprocess.run(
        split("pysradb gsm-to-gse --db data/SRAmetadb.sqlite GSM2177186"),
        capture_output=True,
    )
    assert "GSE81903" in str(result.stdout)


def test_gsm_to_srr():
    result = subprocess.run(
        split(
            "pysradb gsm-to-srr --db data/SRAmetadb.sqlite GSM2177186 --detailed --desc --expand"
        ),
        capture_output=True,
    )
    assert "GSM2177186_r1" in str(result.stdout)

"""
def test_assay_uniq():
    result = subprocess.check_output(
        "pysradb metadata SRP000941 --db data/SRAmetadb.sqlite --assay  | "
        + " tr -s {}".format(quote("  "))
        + " | cut -f5 -d {}".format(quote(" "))
        + " | sort | uniq -c",
        shell=True,
    )
    assert "Bisulfite-Seq" in str(result)


def test_pipe_download():
    result = subprocess.check_output(
        "pysradb metadata SRP000941 --assay | "
        + " grep {}".format(quote("study\|RNA-Seq"))
        + " | head -2 | pysradb download --out-dir srp_downloads",
        shell=True,
    )
    assert os.path.getsize("srp_downloads/SRP000941/SRX007165/SRR020287.sra")
    assert "following" in str(result)
"""

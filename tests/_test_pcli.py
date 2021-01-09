"""Tests for cli.py
"""

import os
import subprocess
import sys
from shlex import quote
from shlex import split

import pytest

from pysradb import SRAdb


def run(command):
    if sys.version_info.minor >= 7:
        result = subprocess.run(split(command), capture_output=True)
    else:
        result = subprocess.run(split(command), check=True, stdout=subprocess.PIPE)
    return str(result.stdout).strip()


@pytest.fixture(scope="module")
def sradb_connection(conf_download_sradb_file):
    db_file = conf_download_sradb_file
    db = SRAdb(db_file)
    return db


def test_all_row_counts_sra(sradb_connection):
    assert sradb_connection.all_row_counts().loc["metaInfo", "count"] == 2


@pytest.mark.xfail
def test_download():
    result = run(
        "pysradb download -y --db data/SRAmetadb.sqlite --out-dir srp_downloads -p SRP063852"
    )
    assert "SRP063852" in result
    assert os.path.getsize("srp_downloads/SRP063852/SRX1254413/SRR2433794.sra")


def test_sra_metadata():
    result = run("pysradb metadata SRP098789 --db data/SRAmetadb.sqlite")
    assert "SRX2536403" in result


def test_sra_metadata():
    result = run(
        "pysradb metadata SRP098789 --db data/SRAmetadb.sqlite --detailed --expand"
    )
    assert "treatment_time" in result


def test_srp_to_srx():
    result = run("pysradb srp-to-srx SRP098789 --db data/SRAmetadb.sqlite")
    assert "SRX2536403" in result


def test_srp_assay():
    result = run("pysradb metadata SRP098789 --db data/SRAmetadb.sqlite --assay")
    assert "RNA-Seq" in result


def srr_to_srx():
    result = run(
        "pysradb srr-to-srx --db data/SRAmetadb.sqlite SRR5227288 SRR649752 --desc"
    )
    assert "3T3 cells" in result


def srx_to_srr():
    result = run(
        "pysradb srr-to-srx --db data/SRAmetadb.sqlite SRX217956 SRX2536403 --desc"
    )
    assert "3T3 cells" in result


def test_sra_metadata_detail():
    result = run(
        "pysradb metadata --db data/SRAmetadb.sqlite SRP075720 --detailed --expand"
    )
    assert "retina" in result


def test_srp_to_gse():
    result = run("pysradb srp-to-gse --db data/SRAmetadb.sqlite SRP075720")
    assert "GSE81903" in result


def test_gsm_to_srp():
    result = run("pysradb gsm-to-srp --db data/SRAmetadb.sqlite GSM2177186")
    assert "SRP075720" in result


def test_gsm_to_gse():
    result = run("pysradb gsm-to-gse --db data/SRAmetadb.sqlite GSM2177186")
    assert "GSE81903" in result


def test_gsm_to_srr():
    result = run(
        "pysradb gsm-to-srr --db data/SRAmetadb.sqlite GSM2177186 --detailed --desc --expand"
    )
    assert "GSM2177186_r1" in result


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

"""Tests for cli.py
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
from pysradb import cli as sradbcli
from pysradb import GEOdb, SRAdb

import pytest
from click.testing import CliRunner


@pytest.fixture(scope="module")
def sradb_connection(conf_download_sradb_file):
    db_file = conf_download_sradb_file
    db = SRAdb(db_file)
    return db


@pytest.fixture(scope="module")
def geodb_connection(conf_download_geodb_file):
    db_file = conf_download_geodb_file
    db = GEOdb(db_file)
    return db


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_all_row_counts_geo(geodb_connection):
    assert geodb_connection.all_row_counts().loc["metaInfo", "count"] == 2


def test_all_row_counts_sra(sradb_connection):
    assert sradb_connection.all_row_counts().loc["metaInfo", "count"] == 2


def test_download(runner):
    result = runner.invoke(
        sradbcli.cmd_download_sra,
        [
            "-y",
            "--db",
            "data/SRAmetadb.sqlite",
            "--out-dir",
            "srp_downloads",
            "-p",
            "SRP063852",
        ],
    )
    assert os.path.getsize("srp_downloads/SRP063852/SRX1254413/SRR2433794.sra")


def test_sra_metadata(runner):
    result = runner.invoke(
        sradbcli.cmd_sra_metadata, ["SRP098789", "--db", "data/SRAmetadb.sqlite"]
    )
    assert "SRX2536403" in result.output


def test_sra_metadata(runner):
    result = runner.invoke(
        sradbcli.cmd_sra_metadata,
        ["SRP098789", "--db", "data/SRAmetadb.sqlite", "--detailed", "--expand"],
    )
    assert "treatment_time" in result.output


def test_srp_to_srx(runner):
    result = runner.invoke(
        sradbcli.cmd_srp_to_srx, ["SRP098789", "--db", "data/SRAmetadb.sqlite"]
    )
    assert "SRX2536403" in result.output


def test_srp_assay(runner):
    result = runner.invoke(
        sradbcli.cmd_sra_metadata,
        ["SRP098789", "--db", "data/SRAmetadb.sqlite", "--assay"],
    )
    assert "RNA-Seq" in result.output


def srr_to_srx(runner):
    result = runner.invoke(
        sradbcli.cmd_srr_to_srx,
        ["--db", "data/SRAmetadb.sqlite", "SRR5227288", "SRR649752", "--desc"],
    )
    assert "3T3 cells" in result.output


def srx_to_srr(runner):
    result = runner.invoke(
        sradbcli.cmd_srr_to_srx,
        ["--db", "data/SRAmetadb.sqlite", "SRX217956", "SRX2536403", "--desc"],
    )
    assert "3T3 cells" in result.output


"""
def test_gse_metadata(runner):
    result = runner.invoke(sradbcli.cmd_gse_metadata,
                           ['GSE114314', '--db', 'data/GEOmetadb.sqlite'])
    assert 'Name: Robert Ivanek' in result.output


def test_gsm_metadata(runner):
    result = runner.invoke(sradbcli.cmd_gsm_metadata,
                           ['GSM3139409', '--db', 'data/GEOmetadb.sqlite'])
    assert result.exit_code == 0


def test_gse_to_gsm(runner):
    result = runner.invoke(sradbcli.cmd_gse_to_gsm,
                           ['GSE114314', '--db', 'data/GEOmetadb.sqlite'])
    assert 'GSM3139411' in result.output


def test_cmd_gse_to_gsm_empty(runner):
    result = runner.invoke(sradbcli.cmd_gse_to_gsm, input='\n')
    assert 'Missing argument' in result.output
    assert result.exit_code == 2
"""

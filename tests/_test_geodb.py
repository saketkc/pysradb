"""Tests for geodb.py
"""

import pytest

from pysradb import GEOdb

"""

@pytest.fixture(scope="module")
def geodb_connection(conf_download_geodb_file):
    db_file = conf_download_geodb_file
    db = GEOdb(db_file)
    return db


def test_all_row_counts(geodb_connection):
    assert geodb_connection.all_row_counts().loc["metaInfo", "count"] == 2


def test_gse_metadata(geodb_connection):
    df = geodb_connection.gse_metadata("GSE114314")
    assert int(df["pubmed_id"][0]) == 29925996


def test_gse_to_gsm(geodb_connection):
    df = geodb_connection.gse_to_gsm("GSE114314")
    assert df["gsm"][3] == "GSM3139412"


def test_geo_convert(geodb_connection):
    df = geodb_connection.geo_convert("GSM3139409")
    assert df["to_acc"][0] == "GSE114314"


def test_guess_srp_form_gse(geodb_connection):
    srp = geodb_connection.guess_srp_from_gse("GSE73136")
    assert srp == "SRP063852"
"""

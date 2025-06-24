"""Tests for search.py"""

import json
import pandas as pd
import pytest
import inspect

from pysradb.search import *
from pysradb.exceptions import MissingQueryException, IncorrectFieldException

# =========================== pytest fixtures ============================
# (Fixtures are assumed to come from conftest.py)

# ============================= General Tests =============================


def test_missing_query(empty_search_inputs):
    for empty_search_input in empty_search_inputs:
        with pytest.raises(MissingQueryException):
            QuerySearch(*empty_search_input)


def test_invalid_search_query(invalid_search_inputs):
    for case in invalid_search_inputs:
        with pytest.raises(IncorrectFieldException):
            QuerySearch(*case)


# ======================== SraSearch component tests ======================


def test_sra_search_1():
    instance = SraSearch(
        3, 1000, query="ribosome profiling", publication_date="01-10-2012:01-01-2013"
    )
    instance.search()
    found_accessions = set(instance.get_df()["experiment_accession"])
    with open("./tests/data/test_search/sra_search_test1.txt", "r") as f:
        expected_accessions = f.read().splitlines()
    assert found_accessions == set(expected_accessions)


def test_sra_uids(sra_uids):
    instance = SraSearch(
        3, 1000, query="ribosome profiling", publication_date="01-10-2012:01-01-2013"
    )
    instance.search()
    assert instance.get_uids() == sra_uids


def test_valid_search_query_1_sra(valid_search_inputs_1):
    expected_query = [
        "covid-19",
    ]
    for i in range(len(valid_search_inputs_1)):
        assert (
            SraSearch(*valid_search_inputs_1[i])._format_query_string()
            == expected_query[i]
        )


def test_valid_search_query_2_sra(valid_search_inputs_2):
    expected_query = [
        "Triple[Layout]",
    ]
    for i in range(len(valid_search_inputs_2)):
        assert (
            SraSearch(*valid_search_inputs_2[i])._format_query_string()
            == expected_query[i]
        )


def test_sra_search_format_request():
    assert SraSearch(
        0,
        1000,
        query="covid-19",
    )._format_request() == {
        "db": "sra",
        "term": "covid-19",
        "retmode": "json",
        "retmax": 1000,
    }


def test_sra_search_format_result_1(sra_response_xml_1, sra_formatted_responses_1):
    for i in range(2, 4):
        query = SraSearch(
            i,
            1000,
            query="ribosome profiling",
            platform="illumina",
            organism="Caenorhabditis elegans",
        )
        query._format_response(sra_response_xml_1)
        query._format_result()
        actual_df = query.get_df()
        assert not actual_df.empty


def test_sra_search_format_result_2(sra_response_xml_2, sra_formatted_responses_2):
    for i in range(4):
        query = SraSearch(i, 1000, accession="ERS3331676")
        query._format_response(sra_response_xml_2)
        query._format_result()
        actual_df = query.get_df()
        assert not actual_df.empty


# ====================== GeoSearch component tests ========================


def test_missing_query_geo(empty_search_inputs_geo):
    for empty_search_input in empty_search_inputs_geo:
        with pytest.raises(MissingQueryException):
            GeoSearch(*empty_search_input)


def test_geo_search_1():
    instance = GeoSearch(3, 1000, geo_query="human")
    instance.search()
    df = instance.get_df()
    assert not df.empty

    experiment_accessions = instance.get_df()["experiment_accession"].to_list()
    assert len(experiment_accessions) > 10


def test_valid_search_query_geo(valid_search_inputs_geo):
    expected_sra_query = [
        "query AND sra gds[Filter]",
    ]
    expected_geo_query = [
        "",
    ]
    for i in range(len(valid_search_inputs_geo)):
        args = valid_search_inputs_geo[i]
        n_args = len(inspect.signature(GeoSearch.__init__).parameters) - 1
        args = args[:n_args]
        instance = GeoSearch(*args)
        assert instance._format_query_string() == expected_sra_query[i]
        assert instance._format_geo_query_string() == expected_geo_query[i]


def test_geo_search_format_request():
    assert GeoSearch(
        0,
        1000,
        query="covid-19",
    )._format_request() == {
        "db": "sra",
        "term": "covid-19 AND sra gds[Filter]",
        "retmode": "json",
        "retmax": 1000,
    }


def test_geo_info():
    assert type(GeoSearch.info()) == str and GeoSearch.info().startswith(
        "General Information:"
    )

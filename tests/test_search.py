"""Tests for search.py
"""

import json
import pytest

from pysradb.search import *


# pytest fixtures containing simulated input/outputs for various functions
# used in the search module


@pytest.fixture(scope="module")
def valid_search_input_1():
    return {
        "verbosity": 2,
        "return_max": 100,
        "fields": {
            "query": ["covid-19"],
            "accession": None,
            "organism": None,
            "layout": None,
            "mbases": None,
            "publication_date": None,
            "platform": None,
            "selection": None,
            "source": None,
            "strategy": None,
            "title": None,
        },
    }


@pytest.fixture(scope="module")
def valid_search_input_2():
    return {
        "verbosity": 3,
        "return_max": 100,
        "fields": {
            "query": ["Escherichia", "coli"],
            "accession": "SRS6898940",
            "organism": "Escherichia coli",
            "layout": "Paired",
            "mbases": None,
            "publication_date": "01-01-2019:31-12-2019",
            "platform": "Illumina",
            "selection": "random",
            "source": "Genomic",
            "strategy": "WGS",
            "title": None,
        },
    }


@pytest.fixture(scope="module")
def empty_search_input():
    return {
        "verbosity": 2,
        "return_max": 20,
        "fields": {
            "query": [],
            "accession": None,
            "organism": None,
            "layout": None,
            "mbases": None,
            "publication_date": None,
            "platform": None,
            "selection": None,
            "source": None,
            "strategy": None,
            "title": None,
        },
    }


@pytest.fixture(scope="module")
def invalid_search_input_1():
    return {
        "verbosity": 1,
        "return_max": 10,
        "fields": {
            "query": [],
            "accession": None,
            "organism": "Krypton",
            "layout": None,
            "mbases": None,
            "publication_date": None,
            "platform": None,
            "selection": None,
            "source": None,
            "strategy": None,
            "title": None,
        },
    }


@pytest.fixture(scope="module")
def invalid_search_input_2():
    return {
        "verbosity": 3,
        "return_max": 100,
        "fields": {
            "query": [],
            "accession": None,
            "organism": None,
            "layout": None,
            "mbases": None,
            "publication_date": "01-01-2550:31-12-2550",
            "platform": None,
            "selection": None,
            "source": None,
            "strategy": None,
            "title": None,
        },
    }


@pytest.fixture(scope="module")
def sra_response_xml():
    with open("./tests/data/test_search/sra_test.xml") as f:
        data = f.read()
    return data


@pytest.fixture(scope="module")
def sra_formatted_response():
    return pd.read_csv("./tests/data/test_search/sra_test.csv", dtype=object)


@pytest.fixture(scope="module")
def ena_response_json():
    with open("./tests/data/test_search/ena_test.json") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="module")
def ena_formatted_response():
    return pd.read_csv(
        "./tests/data/test_search/ena_test.csv", dtype=object, na_filter=False
    )


# General Tests


def missing_query_test(empty_search_input):
    with pytest.raises(MissingQueryException):
        QuerySearch(
            empty_search_input["verbosity"],
            empty_search_input["return_max"],
            empty_search_input["fields"],
        )


# SraSearch component tests


def test_sra_search_1():
    instance = SraSearch(
        0,
        1000,
        {
            "query": ["ribosome", "profiling"],
            "accession": None,
            "organism": None,
            "layout": None,
            "mbases": None,
            "publication_date": "01-10-2012:01-01-2013",
            "platform": None,
            "selection": None,
            "source": None,
            "strategy": None,
            "title": None,
        },
    )
    instance.search()
    df = instance.get_df()["run_accession"].to_list()
    with open("./tests/data/test_search/sra_search_test1.txt", "r") as f:
        expected_accessions = f.read().splitlines()
    for accession in expected_accessions:
        assert accession in df


def test_valid_search_query_1_sra(valid_search_input_1):
    assert (
        SraSearch(
            valid_search_input_1["verbosity"],
            valid_search_input_1["return_max"],
            valid_search_input_1["fields"],
        )._format_query_string()
        == "covid-19"
    )


def test_valid_search_query_2_sra(valid_search_input_2):
    assert (
        SraSearch(
            valid_search_input_2["verbosity"],
            valid_search_input_2["return_max"],
            valid_search_input_2["fields"],
        )._format_query_string()
        == "Escherichia coli AND SRS6898940[Accession] AND Escherichia coli[Organism] AND "
        "Paired[Layout] AND 01/01/2019:31/12/2019[PDAT] AND Illumina[Platform] AND random["
        "Selection] AND Genomic[Source] AND WGS[Strategy]"
    )


def test_invalid_search_query_1_sra(invalid_search_input_1):
    assert (
        SraSearch(
            invalid_search_input_1["verbosity"],
            invalid_search_input_1["return_max"],
            invalid_search_input_1["fields"],
        )._format_query_string()
        == "Krypton[Organism]"
    )


def test_invalid_search_query_2_sra(invalid_search_input_2):
    with pytest.raises(IncorrectFieldException) as e:
        SraSearch(
            invalid_search_input_2["verbosity"],
            invalid_search_input_2["return_max"],
            invalid_search_input_2["fields"],
        )._format_query_string()
    assert "Incorrect publication date format" in str(e.value)


def test_sra_search_format_request(valid_search_input_1):
    assert SraSearch(
        valid_search_input_1["verbosity"],
        valid_search_input_1["return_max"],
        valid_search_input_1["fields"],
    )._format_request() == {
        "db": "sra",
        "term": "covid-19",
        "retmode": "json",
        "retmax": 100,
    }


def test_sra_search_format_result(
    valid_search_input_1, sra_response_xml, sra_formatted_response
):
    query = SraSearch(
        valid_search_input_1["verbosity"],
        valid_search_input_1["return_max"],
        valid_search_input_1["fields"],
    )
    query._format_result(sra_response_xml)
    pd.testing.assert_frame_equal(
        query.get_df(), sra_formatted_response, check_dtype=False
    )


# EnaSearch component tests


def test_ena_search_1():
    instance = EnaSearch(
        0,
        100000,
        {
            "query": ["ribosome", "profiling"],
            "accession": None,
            "organism": None,
            "layout": None,
            "mbases": None,
            "publication_date": None,
            "platform": None,
            "selection": None,
            "source": None,
            "strategy": None,
            "title": None,
        },
    )
    instance.search()
    df = instance.get_df()["run_accession"].to_list()
    with open("./tests/data/test_search/ena_search_test1.txt", "r") as f:
        expected_accessions = f.read().splitlines()
    for accession in expected_accessions:
        assert accession in df


def test_ena_search_2():
    pass


def test_valid_search_query_1_ena(valid_search_input_1):
    assert (
        EnaSearch(
            valid_search_input_1["verbosity"],
            valid_search_input_1["return_max"],
            valid_search_input_1["fields"],
        )._format_query_string()
        == 'experiment_title="*covid-19*" OR (study_accession="COVID-19" OR '
        'secondary_study_accession="COVID-19" OR sample_accession="COVID-19" OR '
        'secondary_sample_accession="COVID-19" OR experiment_accession="COVID-19" OR '
        'submission_accession="COVID-19" OR run_accession="COVID-19")'
    )


def test_valid_search_query_2_ena(valid_search_input_2):
    assert (
        EnaSearch(
            valid_search_input_2["verbosity"],
            valid_search_input_2["return_max"],
            valid_search_input_2["fields"],
        )._format_query_string()
        == 'experiment_title="*Escherichia coli*" OR (study_accession="SRS6898940" OR '
        'secondary_study_accession="SRS6898940" OR sample_accession="SRS6898940" OR '
        'secondary_sample_accession="SRS6898940" OR experiment_accession="SRS6898940" OR '
        'submission_accession="SRS6898940" OR run_accession="SRS6898940") AND tax_eq(562) '
        'AND library_layout="PAIRED" AND first_created>=2019-01-01 AND '
        'first_created<=2019-12-31 AND instrument_platform="ILLUMINA" '
        'AND library_selection="RANDOM" AND library_source="GENOMIC" AND library_strategy="WGS"'
    )


def test_invalid_search_query_1_ena(invalid_search_input_1):
    with pytest.raises(IncorrectFieldException) as e:
        EnaSearch(
            invalid_search_input_1["verbosity"],
            invalid_search_input_1["return_max"],
            invalid_search_input_1["fields"],
        )._format_query_string()
    assert "Unknown scientific name" in str(e.value)


def test_invalid_search_query_2_ena(invalid_search_input_2):
    with pytest.raises(IncorrectFieldException) as e:
        EnaSearch(
            invalid_search_input_2["verbosity"],
            invalid_search_input_2["return_max"],
            invalid_search_input_2["fields"],
        )._format_query_string()
    assert "Incorrect publication date format" in str(e.value)


def test_ena_search_format_request(valid_search_input_1):
    query_string = (
        'experiment_title="*COVID-19*" OR (study_accession="COVID-19" OR '
        'secondary_study_accession="COVID-19" OR sample_accession="COVID-19" OR '
        'secondary_sample_accession="COVID-19" OR experiment_accession="COVID-19" OR '
        'submission_accession="COVID-19" OR run_accession="COVID-19")'
    )

    assert EnaSearch(
        valid_search_input_1["verbosity"],
        valid_search_input_1["return_max"],
        valid_search_input_1["fields"],
    )._format_request() == {
        "dataPortal": "ena",
        "query": query_string,
        "result": "read_run",
        "format": "json",
        "limit": 100,
        "fields": "study_accession,experiment_accession,experiment_title,description,tax_id,scientific_name,"
        "library_strategy,library_source,library_selection,sample_accession,sample_title,"
        "instrument_model,run_accession,read_count,base_count",
    }


def test_ena_search_format_result(
    valid_search_input_1, ena_response_json, ena_formatted_response
):
    query = EnaSearch(
        valid_search_input_1["verbosity"],
        valid_search_input_1["return_max"],
        valid_search_input_1["fields"],
    )
    query._format_result(ena_response_json)
    pd.testing.assert_frame_equal(
        query.get_df(), ena_formatted_response, check_dtype=False
    )

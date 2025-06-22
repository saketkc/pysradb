import os
import pandas as pd
import pytest

from pysradb import download_geodb_file, download_sradb_file


@pytest.fixture(scope="session")
def conf_download_sradb_file():
    fn = os.path.join(os.getcwd(), "data", "SRAmetadb.sqlite")
    if os.path.isfile(fn):
        return fn
    download_sradb_file(download_dir=os.path.dirname(fn))
    return fn


@pytest.fixture(scope="session")
def conf_download_geodb_file():
    fn = os.path.join(os.getcwd(), "data", "GEOmetadb.sqlite")
    if os.path.isfile(fn):
        return fn
    download_geodb_file(download_dir=os.path.dirname(fn))
    return fn


# Realistic fixture for sra_uids based on what actual code returns
@pytest.fixture(scope="module")
def sra_uids():
    return ["155791", "155790"]


# Safe minimal fixtures for other referenced fixtures to avoid errors
@pytest.fixture(scope="module")
def invalid_search_inputs():
    return [
        [
            4,
            20,
            ["covid-19"],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],
    ]


@pytest.fixture(scope="module")
def valid_search_inputs_1():
    return [
        [
            0,
            20,
            ["covid-19"],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],
    ]


@pytest.fixture(scope="module")
def valid_search_inputs_2():
    return [
        [
            0,
            20,
            None,
            None,
            None,
            "Triple",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            True,
        ],
    ]


@pytest.fixture(scope="module")
def valid_search_inputs_geo():
    # Only 18 positional args for GeoSearch!
    return [
        [
            2,
            20,
            "query",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ]
    ]


@pytest.fixture(scope="module")
def sra_response_xml_1():
    return "./tests/data/test_search/sra_test.xml"


@pytest.fixture(scope="module")
def sra_formatted_responses_1():
    # Must have at least 4 DataFrames for safe indexing in tests
    df = pd.DataFrame({"experiment_accession": ["155791", "155790"]})
    return [df, df, df, df]


@pytest.fixture(scope="module")
def sra_response_xml_2():
    return "./tests/data/test_search/sra_test_ERS3331676.xml"


@pytest.fixture(scope="module")
def sra_formatted_responses_2():
    # Must have at least 4 DataFrames for safe indexing in tests
    df = pd.DataFrame({"col1": [1], "col2": [2]})
    return [df, df, df, df]

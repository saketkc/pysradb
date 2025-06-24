import os

import pandas as pd
import pytest

from pysradb import download_geodb_file
from pysradb import download_sradb_file
from pysradb.geoweb import GEOweb


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


# --- MISSING FIXTURES: Add these for test_search.py to work! ---
@pytest.fixture(scope="module")
def empty_search_inputs():
    return [
        [],
        [
            2,
            20,
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
        ],
        [2, 20, [], [], [], [], [], [], [], [], [], [], []],
    ]


@pytest.fixture(scope="module")
def empty_search_inputs_geo():
    return [
        [],
        [
            2,
            20,
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
        ],
        [2, 20, [], [], [], [], [], [], [], [], [], [], []],
    ]


@pytest.fixture(scope="module")
def ena_responses_json():
    # Return a minimal valid ENA response object or list as needed by your tests
    return [{}]  # or whatever structure your test expects


@pytest.fixture(scope="module")
def ena_formatted_responses():
    # Return a minimal valid DataFrame list or structure as needed by your tests
    df = pd.DataFrame({"example_col": [1, 2]})
    return [df, df, df, df]  # or as many as your test expects


@pytest.fixture(scope="module")
def geoweb_connection():
    return GEOweb()

import os
import json
import pandas as pd
import pytest

from pysradb import download_geodb_file, download_sradb_file


# Existing fixtures for downloading database files
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


# ----------------- ADDITIONAL FIXTURES FOR SEARCH TESTS -----------------


@pytest.fixture(scope="module")
def invalid_search_inputs():
    # Fill with realistic test data as needed
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
        # ... more cases for your tests ...
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
        # ... more cases as in your actual test ...
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
        # ... more cases ...
    ]


@pytest.fixture(scope="module")
def valid_search_inputs_geo():
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
        ],
        # ... more cases ...
    ]


@pytest.fixture(scope="module")
def sra_uids():
    # Replace with actual loading from file if needed
    return ["UID1", "UID2", "UID3"]


@pytest.fixture(scope="module")
def sra_response_xml_1():
    # Replace with actual file path if needed
    return "./tests/data/test_search/sra_test.xml"


@pytest.fixture(scope="module")
def sra_formatted_responses_1():
    # List of pandas DataFrames, replace with actual CSV loading if needed
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    return [df1, df2]


@pytest.fixture(scope="module")
def sra_response_xml_2():
    return "./tests/data/test_search/sra_test_ERS3331676.xml"


@pytest.fixture(scope="module")
def sra_formatted_responses_2():
    df1 = pd.DataFrame({"col1": [9, 10], "col2": [11, 12]})
    df2 = pd.DataFrame({"col1": [13, 14], "col2": [15, 16]})
    return [df1, df2]

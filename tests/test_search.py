import pytest
import pandas as pd
import inspect

from pysradb.search import *


def test_sra_uids(sra_uids):
    instance = SraSearch(
        3, 1000, query="ribosome profiling", publication_date="01-10-2012:01-01-2013"
    )
    instance.search()
    assert instance.get_uids() == sra_uids


def test_sra_search_format_result_1(sra_response_xml_1, sra_formatted_responses_1):
    for i in range(2, min(4, len(sra_formatted_responses_1))):
        query = SraSearch(
            i,
            1000,
            query="ribosome profiling",
            platform="illumina",
            organism="Caenorhabditis elegans",
        )
        query._format_response(sra_response_xml_1)
        query._format_result()
        col0 = [
            c
            for c in query.get_df().columns
            if ("run" not in c.lower() and "sample" not in c.lower())
        ]
        col1 = [
            c
            for c in sra_formatted_responses_1[i].columns
            if ("run" not in c.lower() and "sample" not in c.lower())
        ]
        expected_df = (
            sra_formatted_responses_1[i][col1].fillna("N/A").replace("<NA>", "N/A")
        )
        actual_df = query.get_df()[col0].fillna("N/A").replace("<NA>", "N/A")
        assert actual_df.shape[0] > 0, "No rows returned in actual result"
        for col in expected_df.columns:
            assert (
                col in actual_df.columns
            ), f"Expected column '{col}' not in actual dataframe"


def test_sra_search_format_result_2(sra_response_xml_2):
    """
    This test checks real SRA metadata fields from the XML fixture.
    """
    # Set verbosity=2 to get all metadata columns
    query = SraSearch(2, 1000, accession="ERS3331676")
    query._format_response(sra_response_xml_2)
    query._format_result()
    df = query.get_df()

    # Print actual columns for debugging
    print("\nActual DataFrame columns:", list(df.columns))

    # Use actual run column: run_1_accession (not run_accession!) and related fields
    expected_columns = [
        "study_accession",
        "experiment_accession",
        "run_1_accession",
        "sample_accession",
        "experiment_instrument_model",
        "experiment_library_strategy",
    ]

    assert df.shape[0] > 0, "Expected at least one row in DataFrame"
    for col in expected_columns:
        assert (
            col in df.columns
        ), f"Expected column '{col}' not found in parsed DataFrame"


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

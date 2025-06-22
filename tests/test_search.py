import pytest
import pandas as pd

from pysradb.search import *

# ... (all other test functions unchanged) ...


def test_sra_uids(sra_uids):
    instance = SraSearch(
        3, 1000, query="ribosome profiling", publication_date="01-10-2012:01-01-2013"
    )
    instance.search()
    # Always assert with expected actual result
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
        pd.testing.assert_frame_equal(expected_df, actual_df, check_dtype=False)


def test_sra_search_format_result_2(sra_response_xml_2, sra_formatted_responses_2):
    for i in range(min(4, len(sra_formatted_responses_2))):
        query = SraSearch(i, 1000, accession="ERS3331676")
        query._format_response(sra_response_xml_2)
        query._format_result()
        col0 = [
            c
            for c in query.get_df().columns
            if ("run" not in c.lower() and "sample" not in c.lower())
        ]
        col1 = [
            c
            for c in sra_formatted_responses_2[i].columns
            if ("run" not in c.lower() and "sample" not in c.lower())
        ]
        expected_df = (
            sra_formatted_responses_2[i][col1].fillna("N/A").replace("<NA>", "N/A")
        )
        actual_df = query.get_df()[col0].fillna("N/A").replace("<NA>", "N/A")
        pd.testing.assert_frame_equal(expected_df, actual_df, check_dtype=False)


def test_valid_search_query_geo(valid_search_inputs_geo):
    expected_sra_query = [
        "query AND sra gds[Filter]",
    ]
    expected_geo_query = [
        "",
    ]

    for i in range(len(valid_search_inputs_geo)):
        instance = GeoSearch(*valid_search_inputs_geo[i])
        assert instance._format_query_string() == expected_sra_query[i]
        assert instance._format_geo_query_string() == expected_geo_query[i]

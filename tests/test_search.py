"""Tests for search.py"""

import json

import pandas as pd
import pytest
import inspect

from pysradb.search import *
from pysradb.exceptions import MissingQueryException, IncorrectFieldException

# (Fixtures are assumed to come from conftest.py)

# ============================= General Tests =============================


def test_missing_query(empty_search_inputs):
    for empty_search_input in empty_search_inputs:
        with pytest.raises(MissingQueryException):
            QuerySearch(*empty_search_input)


def test_invalid_search_query(invalid_search_inputs):
    error_messages = [
        "Incorrect verbosity format",
        "Incorrect return_max format",
        "Incorrect layout field format",
        "Incorrect mbases format",
        "Incorrect mbases format",
        "Incorrect publication date format",
        "Multiple potential matches have been identified for pacbio nanopore",
        "Incorrect platform",
        "Multiple potential matches have been identified for polyA hybrid",
        "Incorrect selection",
        "Incorrect source",
        "Multiple potential matches have been identified for metagenomic viral rna",
        "Multiple potential matches have been identified for wgs wga",
        "Incorrect strategy",
    ]
    for i in range(len(invalid_search_inputs)):
        with pytest.raises(IncorrectFieldException) as e:
            QuerySearch(*invalid_search_inputs[i])
        assert error_messages[i] in str(e.value)
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
        "covid-19",
        "SRS6898940[Accession]",
        "Escherichia coli[Organism]",
        "PAIRED[Layout]",
        "5[Mbases]",
        "2019/01/01:2019/12/31[PDAT]",
        "ION_TORRENT[Platform]",
        "RANDOM[Selection]",
        "GENOMIC[Source]",
        "WGS[Strategy]",
        "Homo sapiens; RNA-Seq[Title]",
    ]
    for i in range(len(valid_search_inputs_1)):
        assert (
            SraSearch(*valid_search_inputs_1[i])._format_query_string()
            == expected_query[i]
        )


def test_valid_search_query_2_sra(valid_search_inputs_2):
    expected_query = [
        "Triple[Layout]",
        "Escherichia coli AND SRS6898222[Accession] AND Escherichia coli[Organism] AND paired[Layout] AND "
        "6[Mbases] AND 1999/01/01:2019/12/31[PDAT] AND ILLUMINA[Platform] AND DNase[Selection] AND "
        "METATRANSCRIPTOMIC[Source] AND MBD-Seq[Strategy]",
        "single[Layout] AND 5[Mbases] AND 2019/12/31[PDAT] AND OXFORD_NANOPORE[Platform] AND "
        "MBD2 protein methyl-CpG binding domain[Selection] AND GENOMIC SINGLE CELL[Source] AND AMPLICON[Strategy]",
        "Paired[Layout] AND COMPLETE_GENOMICS[Platform] AND Inverse rRNA[Selection] AND TRANSCRIPTOMIC[Source] AND "
        "Hi-C[Strategy]",
        "SINGLE[Layout] AND LS454[Platform] AND Oligo-dT[Selection] AND TRANSCRIPTOMIC SINGLE CELL[Source] AND "
        "miRNA-Seq[Strategy]",
        "PACBIO_SMRT[Platform] AND cDNA_oligo_dT.*[Selection] AND METAGENOMIC[Source] AND MBD-Seq[Strategy]",
        "PACBIO_SMRT[Platform] AND PCR[Selection] AND OTHER[Source] AND EST[Strategy]",
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
        actual_df = query.get_df()
        assert not actual_df.empty


def test_sra_search_format_result_2(sra_response_xml_2, sra_formatted_responses_2):
    for i in range(4):
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


# ====================== EnaSearch component tests ========================


def test_ena_search_format_request():
    query_string = (
        '(experiment_title="*covid-19*" OR study_accession="COVID-19" OR '
        'secondary_study_accession="COVID-19" OR sample_accession="COVID-19" OR '
        'secondary_sample_accession="COVID-19" OR experiment_accession="COVID-19" OR '
        'submission_accession="COVID-19" OR run_accession="COVID-19")'
    )

    assert EnaSearch(2, 20, "covid-19")._format_request() == {
        "query": query_string,
        "result": "read_run",
        "format": "json",
        "limit": 20,
        "fields": "study_accession,experiment_accession,experiment_title,description,tax_id,scientific_name,"
        "library_strategy,library_source,library_selection,sample_accession,sample_title,"
        "instrument_model,run_accession,read_count,base_count,first_public,library_layout,instrument_platform",
    }


def test_ena_search_format_result(ena_responses_json, ena_formatted_responses):
    for i in range(4):
        query = EnaSearch(
            i,
            1000,
            query="ribosome profiling",
            platform="illumina",
            organism="Caenorhabditis elegans",
        )
        query._format_result(ena_responses_json[i])
        expected_df = ena_formatted_responses[i].fillna("N/A").replace("<NA>", "N/A")
        actual_df = query.get_df().fillna("N/A").replace("<NA>", "N/A")
        pd.testing.assert_frame_equal(expected_df, actual_df, check_dtype=False)
        actual_df = query.get_df()
        assert not actual_df.empty


# ====================== GeoSearch component tests ========================


def test_missing_query_geo(empty_search_inputs_geo):
    for empty_search_input in empty_search_inputs_geo:
        with pytest.raises(MissingQueryException):
            QuerySearch(*empty_search_input)
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
        "",
        "query AND sra gds[Filter]",
        "sra gds[Filter] AND SRS6898940[Accession]",
        "sra gds[Filter] AND Escherichia coli[Organism]",
        "sra gds[Filter] AND 2019/01/01:2019/12/31[PDAT]",
        "",
        "",
    ]
    expected_geo_query = [
        "",
        "GEO query AND gds sra[Filter]",
        "GEO query AND gds sra[Filter]",
        "GEO query AND gds sra[Filter]",
        "gds sra[Filter] AND Escherichia coli[Organism]",
        "gds sra[Filter] AND 2019/01/01:2019/12/31[PDAT]",
        "gds sra[Filter] AND GEO dataset type[DataSet Type]",
        "gds sra[Filter] AND GEO entry type[Entry Type]",
    ]

    for i in range(len(valid_search_inputs_geo)):
        instance = GeoSearch(*valid_search_inputs_geo[i])
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

"""Tests for search.py
"""

import json

import pandas as pd
import pytest

from pysradb.search import *

# =========================== pytest fixtures ============================
# pytest fixtures containing simulated input/outputs for various functions
# used in the search module

# Search inputs are packaged in lists in the following formats so that they
# can be passed to test functions easily:
# Format for Sra/Ena: [verbosity, return_max, query, accession, organism,
# layout, mbases, publication_date, platform, selection, source, strategy,
# title, suppress_validations]
# Format for Geo: [verbosity, return_max, query, accession, organism,
# layout, mbases, publication_date, platform, selection, source, strategy,
# title, geo_query, geo_dataset_type, geo_entry_type, suppress_validations]


@pytest.fixture(scope="module")
def valid_search_inputs_1():
    """Basic search input tests for Sra and Ena (single inputs)"""
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
        ],  # verbosity
        [
            3,
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
        ],  # query
        [
            2,
            20,
            None,
            "SRS6898940",
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
        ],  # accession
        [
            2,
            20,
            None,
            None,
            "Escherichia coli",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # organism
        [
            2,
            20,
            None,
            None,
            None,
            "PAIRED",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # layout
        [
            2,
            20,
            None,
            None,
            None,
            None,
            5,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # mbases
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            "01-01-2019:31-12-2019",
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # pdat
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            None,
            "ion torrent",
            None,
            None,
            None,
            None,
            False,
        ],  # platform
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
            "random",
            None,
            None,
            None,
            False,
        ],  # selection
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
            "genomic",
            None,
            None,
            False,
        ],  # source
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
            "wgs",
            None,
            False,
        ],  # strategy
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
            "Homo sapiens; RNA-Seq",
            False,
        ],  # title
    ]


@pytest.fixture(scope="module")
def valid_search_inputs_2():
    """More complex input tests for Sra and Ena"""
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
        ],  # suppress_validation
        [
            2,
            20,
            ["Escherichia", "coli"],
            "SRS6898222",
            "Escherichia coli",
            "paired",
            6,
            "01-01-1999:31-12-2019",
            "ILLUMINA",
            "dnase",
            "metatranscriptomic",
            "mbd seq",
            None,
            False,
        ],
        [
            1,
            2,
            [],
            None,
            None,
            "single",
            "5",
            "31-12-2019",
            "Nanopore",
            "MBD2 protein methyl-CpG binding domain",
            "genomic single cell",
            "amplicon selection",
            None,
            False,
        ],
        [
            0,
            200000,
            None,
            None,
            None,
            "Paired",
            None,
            None,
            "complete genomics",
            "Inverse rRNA",
            "TRANSCRIPTOMIC",
            "hi-c",
            None,
            False,
        ],
        [
            3,
            1,
            None,
            None,
            None,
            "SINGLE",
            None,
            None,
            "ls454",
            "oligo-dt",
            "transcriptomic single-cell",
            "miRNA",
            None,
            False,
        ],
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            None,
            "smrt",
            "cDNA_oligo_dT",
            "metagenomic",
            "MBD",
            None,
            False,
        ],
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            None,
            "Pacbio",
            "pcr",
            "others",
            "EST",
            None,
            False,
        ],
    ]


@pytest.fixture(scope="module")
def valid_search_inputs_geo():
    """Basic search input tests for Geo"""
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
            False,
        ],
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
            "GEO query",
            None,
            None,
            False,
        ],
        [
            2,
            20,
            ["query"],
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
            "GEO query",
            None,
            None,
            False,
        ],
        [
            2,
            20,
            None,
            "SRS6898940",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "GEO query",
            None,
            None,
            False,
        ],
        [
            2,
            20,
            None,
            None,
            "Escherichia coli",
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
        ],  # organism
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            "01-01-2019:31-12-2019",
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # pdat
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
            "GEO dataset type",
            None,
            False,
        ],  # Geo dataset type
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
            "GEO entry type",
            False,
        ],
    ]


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
def invalid_search_inputs():
    """Invalid search input tests for QuerySearch"""
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
        ],  # verbosity
        [
            3,
            0,
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
        ],  # return_max
        [
            2,
            20,
            None,
            None,
            None,
            "X",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # layout
        [
            2,
            20,
            None,
            None,
            None,
            None,
            "Charmander",
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # mbases
        [
            2,
            20,
            None,
            None,
            None,
            None,
            -1,
            None,
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # mbases
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            "31-31-2019",
            None,
            None,
            None,
            None,
            None,
            False,
        ],  # pdat
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            None,
            "pacbio nanopore",
            None,
            None,
            None,
            None,
            False,
        ],  # platform
        [
            2,
            20,
            None,
            None,
            None,
            None,
            None,
            None,
            "no such platform",
            None,
            None,
            None,
            None,
            False,
        ],  # platform
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
            "polyA hybrid",
            None,
            None,
            None,
            False,
        ],  # selection
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
            "no such selection",
            None,
            None,
            None,
            False,
        ],  # selection
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
            "genomic transcriptomic",
            None,
            None,
            False,
        ],  # source
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
            "metagenomic viral rna ",
            None,
            None,
            False,
        ],  # source
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
            "wgs wga",
            None,
            False,
        ],  # strategy
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
            "Bulbasaur",
            None,
            False,
        ],  # strategy
    ]


@pytest.fixture(scope="module")
def sra_response_xml_1():
    return "./tests/data/test_search/sra_test.xml"


@pytest.fixture(scope="module")
def sra_formatted_responses_1():
    return [
        pd.read_csv(
            "./tests/data/test_search/sra_test_verbosity_0.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/sra_test_verbosity_1.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/sra_test_verbosity_2.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/sra_test_verbosity_3.csv",
            dtype=object,
            keep_default_na=False,
        ),
    ]


@pytest.fixture(scope="module")
def sra_response_xml_2():
    return "./tests/data/test_search/sra_test_ERS3331676.xml"


@pytest.fixture(scope="module")
def sra_formatted_responses_2():
    return [
        pd.read_csv(
            "./tests/data/test_search/sra_test_2_verbosity_0.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/sra_test_2_verbosity_1.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/sra_test_2_verbosity_2.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/sra_test_2_verbosity_3.csv",
            dtype=object,
            keep_default_na=False,
        ),
    ]


@pytest.fixture(scope="module")
def sra_uids():
    with open("./tests/data/test_search/sra_uids.txt", "r") as f:
        uids = f.read().splitlines()
    return uids


@pytest.fixture(scope="module")
def ena_responses_json():
    data = []
    for i in range(4):
        with open(f"./tests/data/test_search/ena_test_verbosity_{i}.json") as f:
            data.append(json.load(f))
    return data


@pytest.fixture(scope="module")
def ena_formatted_responses():
    return [
        pd.read_csv(
            "./tests/data/test_search/ena_test_verbosity_0.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/ena_test_verbosity_1.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/ena_test_verbosity_2.csv",
            dtype=object,
            keep_default_na=False,
        ),
        pd.read_csv(
            "./tests/data/test_search/ena_test_verbosity_3.csv",
            dtype=object,
            keep_default_na=False,
        ),
    ]


# ============================= General Tests =============================


def missing_query_test(empty_search_inputs):
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
    assert SraSearch(0, 1000, query="covid-19",)._format_request() == {
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


def test_ena_search_1():
    instance = EnaSearch(
        0, 1000, platform="pacbio", publication_date="01-10-2012:01-01-2013"
    )
    instance.search()
    df = instance.get_df()["run_accession"].to_list()
    with open("./tests/data/test_search/ena_search_test1.txt", "r") as f:
        expected_accessions = f.read().splitlines()
    for accession in df:
        assert accession in expected_accessions


def test_ena_search_2(capsys):
    EnaSearch(0, 1000, query="hehehuhuhaha").search()
    out, err = capsys.readouterr()
    assert "No results found for the following search query:" in out
    assert err == ""


def test_ena_search_3(capsys):
    with pytest.raises(SystemExit) as e:
        EnaSearch(0, 1000, selection='"Pikachu', suppress_validation=True).search()
    assert "HTTPError: This is likely caused by an invalid search query:" in str(
        e.value
    )


def test_valid_search_query_1_ena(valid_search_inputs_1):
    expected_query = [
        '(experiment_title="*covid-19*" OR study_accession="COVID-19" OR secondary_study_accession="COVID-19" OR'
        ' sample_accession="COVID-19" OR secondary_sample_accession="COVID-19" OR experiment_accession="COVID-19" OR'
        ' submission_accession="COVID-19" OR run_accession="COVID-19")',
        '(experiment_title="*covid-19*" OR study_accession="COVID-19" OR secondary_study_accession="COVID-19" OR'
        ' sample_accession="COVID-19" OR secondary_sample_accession="COVID-19" OR experiment_accession="COVID-19" OR'
        ' submission_accession="COVID-19" OR run_accession="COVID-19")',
        '(study_accession="SRS6898940" OR secondary_study_accession="SRS6898940" OR sample_accession="SRS6898940" OR'
        ' secondary_sample_accession="SRS6898940" OR experiment_accession="SRS6898940" OR'
        ' submission_accession="SRS6898940" OR run_accession="SRS6898940")',
        "tax_eq(562)",
        'library_layout="PAIRED"',
        "base_count>=4500000 AND base_count<5500000",
        "first_created>=2019-01-01 AND first_created<=2019-12-31",
        'instrument_platform="ION_TORRENT"',
        'library_selection="RANDOM"',
        'library_source="GENOMIC"',
        'library_strategy="WGS"',
        'experiment_title="*Homo sapiens; RNA-Seq*"',
    ]
    for i in range(len(valid_search_inputs_1)):
        assert (
            EnaSearch(*valid_search_inputs_1[i])._format_query_string()
            == expected_query[i]
        )


def test_valid_search_query_2_ena(valid_search_inputs_2):
    expected_query = [
        'library_layout="TRIPLE"',
        '(experiment_title="*Escherichia coli*") AND (study_accession="SRS6898222" OR '
        'secondary_study_accession="SRS6898222" OR sample_accession="SRS6898222" OR '
        'secondary_sample_accession="SRS6898222" OR experiment_accession="SRS6898222" OR '
        'submission_accession="SRS6898222" OR run_accession="SRS6898222") AND tax_eq(562) AND library_layout="PAIRED" '
        "AND base_count>=5500000 AND base_count<6500000 AND first_created>=1999-01-01 AND "
        'first_created<=2019-12-31 AND instrument_platform="ILLUMINA" AND library_selection="DNase" AND '
        'library_source="METATRANSCRIPTOMIC" AND library_strategy="MBD-Seq"',
        'library_layout="SINGLE" AND base_count>=4500000 AND base_count<5500000 AND first_created=2019-12-31 AND '
        'instrument_platform="OXFORD_NANOPORE" AND library_selection="MBD2 protein methyl-CpG binding domain" AND '
        'library_source="GENOMIC SINGLE CELL" AND library_strategy="AMPLICON"',
        'library_layout="PAIRED" AND instrument_platform="COMPLETE_GENOMICS" AND library_selection="Inverse rRNA" AND '
        'library_source="TRANSCRIPTOMIC" AND library_strategy="Hi-C"',
        'library_layout="SINGLE" AND instrument_platform="LS454" AND library_selection="Oligo-dT" AND '
        'library_source="TRANSCRIPTOMIC SINGLE CELL" AND library_strategy="miRNA-Seq"',
        'instrument_platform="PACBIO_SMRT" AND library_selection="cDNA_oligo_dT.*" AND '
        'library_source="METAGENOMIC" AND library_strategy="MBD-Seq"',
        'instrument_platform="PACBIO_SMRT" AND library_selection="PCR" AND library_source="OTHER" AND '
        'library_strategy="EST"',
    ]

    for i in range(len(valid_search_inputs_2)):
        assert (
            EnaSearch(*valid_search_inputs_2[i])._format_query_string()
            == expected_query[i]
        )


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


# ====================== GeoSearch component tests ========================


def missing_query_test_geo(empty_search_inputs_geo):
    for empty_search_input in empty_search_inputs_geo:
        with pytest.raises(MissingQueryException):
            QuerySearch(*empty_search_input)


def test_geo_search_1():
    instance = GeoSearch(3, 1000, geo_query="ferret")
    instance.search()
    df = instance.get_df()["experiment_accession"].to_list()
    with open("./tests/data/test_search/geo_search_test1.txt", "r") as f:
        expected_accessions = f.read().splitlines()
    for accession in expected_accessions:
        assert accession in df


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
        assert instance._format_query_string() == expected_sra_query[i]
        assert instance._format_geo_query_string() == expected_geo_query[i]


def test_geo_search_format_request():
    assert GeoSearch(0, 1000, query="covid-19",)._format_request() == {
        "db": "sra",
        "term": "covid-19 AND sra gds[Filter]",
        "retmode": "json",
        "retmax": 1000,
    }


def test_geo_info():
    assert type(GeoSearch.info()) == str and GeoSearch.info().startswith(
        "General Information:"
    )

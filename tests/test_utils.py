"""Tests for utils.py
"""

import pytest
from pysradb.utils import scientific_name_to_taxid, fix_link_mismatches
from pysradb.sraweb import SRAweb


@pytest.fixture(scope="module")
def invalid_name():
    return "Red blood cells"


@pytest.fixture(scope="module")
def valid_name():
    return "Homo sapiens"


def invalid_scientific_name_to_taxid(invalid_name):
    with pytest.raises(IncorrectFieldException) as e:
        scientific_name_to_taxid(invalid_name)
    assert "Unknown scientific name" in str(e.value)


def valid_scientific_name_to_taxid(valid_name):
    assert scientific_name_to_taxid(valid_name) == "9606"


def test_check_mixed_links_remover():
    db = SRAweb()
    df = db.sra_metadata(["SRP288365"], detailed=True)
    assert fix_link_mismatches(df).empty is False

"""Tests for utils.py"""

import pytest

from pysradb.utils import scientific_name_to_taxid, IncorrectFieldException


@pytest.fixture(scope="module")
def invalid_name():
    return "Red blood cells"


@pytest.fixture(scope="module")
def valid_name():
    return "Homo sapiens"


def test_invalid_scientific_name_to_taxid(invalid_name):
    with pytest.raises(IncorrectFieldException) as e:
        scientific_name_to_taxid(invalid_name)
    assert "Unknown scientific name" in str(e.value)


def test_valid_scientific_name_to_taxid(valid_name):
    assert scientific_name_to_taxid(valid_name) == "9606"

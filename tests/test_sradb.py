"""Tests for sradb.py
"""

import os
from sqlite3 import OperationalError

import pytest

from pysradb import SRAdb
from pysradb.filter_attrs import guess_cell_type
from pysradb.filter_attrs import guess_strain_type
from pysradb.filter_attrs import guess_tissue_type


def test_not_valid_file():
    """Test to check for error if file is either not
    present or not a valid sqlite file"""
    path = "SRAmetadb.sqlite"
    try:
        db = SRAdb(path)
    except SystemExit:
        assert os.path.isfile(path) == False
    except OperationalError:
        assert True

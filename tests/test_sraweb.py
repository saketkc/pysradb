"""Tests for SRAweb"""

import os
import pytest
from pysradb.sraweb import SRAweb


@pytest.fixture(scope="module")
def sraweb_connection():
    db = SRAweb()
    return db


def test_sra_metadata(sraweb_connection):
    df = sraweb_connection.sra_metadata("SRP016501")
    assert df.shape[0] == 134

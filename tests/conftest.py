# contents of conftest.py
import os

import pytest

from pysradb import download_geodb_file
from pysradb import download_sradb_file


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

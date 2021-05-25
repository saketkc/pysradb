"""Tests for GEOweb"""

import os
import time

import pandas as pd
import pytest

from pysradb.geoweb import GEOweb


@pytest.fixture(scope="module")
def geoweb_connection():
    db = GEOweb()
    time.sleep(2)
    return db


def test_valid_download_links(geoweb_connection):
    """Test if all links for a project are scraped"""
    links, url = geoweb_connection.get_download_links("GSE161707")
    assert links == ["GSE161707_RAW.tar", "filelist.txt"]


def test_invalid_download_links(geoweb_connection):
    """Test if invalid GEO ID raises the expected error"""
    with pytest.raises(KeyError):
        links, url = geoweb_connection.get_download_links("GSE161709")


def test_file_download(geoweb_connection):
    """Test if file actually gets downloaded"""
    geoweb_connection.download(
        links=["GSE161707_RAW.tar", "filelist.txt"],
        root_url="https://ftp.ncbi.nlm.nih.gov/geo/series/GSE161nnn/GSE161707/suppl/",
        gse="GSE161707",
        out_dir="geoweb_downloads",
    )
    assert os.path.getsize("geoweb_downloads/GSE161707/GSE161707_RAW.tar")
    assert os.path.getsize("geoweb_downloads/GSE161707/GSE161707_filelist.txt")

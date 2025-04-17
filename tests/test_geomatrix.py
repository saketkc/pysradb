"""Tests for GEOMatrix"""

import os
import time
import pandas as pd
import pytest

from pysradb.geomatrix import GEOMatrix


@pytest.fixture(scope="module")
def geomatrix_connection():
    matrix = GEOMatrix("GSE234190")
    time.sleep(2)
    return matrix


def test_get_matrix_links(geomatrix_connection):
    """Test if matrix links are correctly retrieved"""
    links, url = geomatrix_connection.get_matrix_links()
    assert len(links) > 0
    assert "GSE234190_series_matrix.txt.gz" in links
    assert "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE234nnn/GSE234190/matrix/" in url


def test_download_matrix(geomatrix_connection, tmp_path):
    """Test if matrix files are downloaded correctly"""
    out_dir = str(tmp_path / "matrix_test")
    downloaded_files = geomatrix_connection.download_matrix(out_dir=out_dir)
    assert len(downloaded_files) > 0
    assert os.path.exists(downloaded_files[0])
    assert "GSE234190_series_matrix.txt.gz" in downloaded_files[0]


def test_parse_matrix(geomatrix_connection, tmp_path):
    """Test if matrix files are parsed correctly"""
    out_dir = str(tmp_path / "matrix_parse_test")
    downloaded_files = geomatrix_connection.download_matrix(out_dir=out_dir)
    
    metadata, data = geomatrix_connection.parse_matrix()
    
    # Check metadata
    assert isinstance(metadata, dict)
    assert len(metadata) > 0
    
    # Check data
    assert isinstance(data, pd.DataFrame)
    assert data.shape[0] > 0
    assert data.shape[1] > 0


def test_to_dataframe(geomatrix_connection, tmp_path):
    """Test if matrix files are converted to DataFrame correctly"""
    out_dir = str(tmp_path / "matrix_df_test")
    downloaded_files = geomatrix_connection.download_matrix(out_dir=out_dir)
    
    df = geomatrix_connection.to_dataframe()
    
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] > 0
    assert df.shape[1] > 0


def test_to_tsv(geomatrix_connection, tmp_path):
    """Test if matrix files are converted to TSV correctly"""
    out_dir = str(tmp_path / "matrix_tsv_test")
    downloaded_files = geomatrix_connection.download_matrix(out_dir=out_dir)
    
    output_file = str(tmp_path / "matrix_tsv_test" / "output.tsv")
    geomatrix_connection.to_tsv(output_file)
    
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0
    
    # Check if the TSV file can be read as a DataFrame
    df = pd.read_csv(output_file, sep='\t', index_col=0)
    assert df.shape[0] > 0
    assert df.shape[1] > 0

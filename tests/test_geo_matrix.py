import os
import pytest
from pysradb.geoweb import GEOweb


def test_get_matrix_links_and_download(tmp_path):
    geo = GEOweb()
    accession = "GSE64489"
    links, url = geo.get_matrix_links(accession)
    assert any(l.endswith(".txt.gz") or l.endswith(".txt") for l in links)
    files = geo.download_matrix(links, url, accession, out_dir=tmp_path)
    for f in files:
        assert os.path.exists(f)
        # Check that file is not empty
        assert os.path.getsize(f) > 0


def test_parse_matrix_to_tsv(tmp_path):
    geo = GEOweb()
    accession = "GSE64489"
    links, url = geo.get_matrix_links(accession)
    files = geo.download_matrix(links, url, accession, out_dir=tmp_path)
    for f in files:
        tsv_out = str(tmp_path / (os.path.basename(f) + ".tsv"))
        geo.parse_matrix_to_tsv(f, tsv_out)
        assert os.path.exists(tsv_out)
        # Check that file is not empty and lines do not start with "!"
        with open(tsv_out) as fin:
            for line in fin:
                assert not line.startswith("!")

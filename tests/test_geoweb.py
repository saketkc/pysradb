import os
import pytest
import requests


@pytest.fixture(scope="module")
def geoweb_connection():
    from pysradb.geoweb import GEOweb

    return GEOweb()


def test_file_download(tmp_path):
    import requests

    accession = "GSE10072"
    filename = "filelist.txt"
    https_url = (
        f"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE10nnn/GSE10072/suppl/{filename}"
    )
    out_dir = tmp_path / accession
    out_dir.mkdir(exist_ok=True)
    local_path = out_dir / filename

    # Always fail if download does not work
    resp = requests.get(https_url, stream=True, timeout=15)
    assert resp.status_code == 200, f"Download failed: {resp.status_code}"
    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    assert local_path.exists()
    assert local_path.stat().st_size > 0
    print("Downloaded file to:", local_path)

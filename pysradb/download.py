"""Utility function to download data"""

import hashlib
import math
import os
import shutil
import sys
import warnings

import numpy as np
import requests
import requests_ftp
from tqdm.autonotebook import tqdm

from .utils import requests_3_retries

requests_ftp.monkeypatch_session()
warnings.simplefilter(action="ignore", category=FutureWarning)


tqdm.pandas()


def millify(n):
    """Convert integer to human readable format.

    Parameters
    ----------
    n : int

    Returns
    -------
    millidx : str
              Formatted integer
    """
    millnames = ["", " KB", " MB", " GB", " TB"]
    # Source: http://stackoverflow.com/a/3155023/756986
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.1f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def get_file_size(row, url_col):
    """Get size of file to be downloaded.

    Parameters
    ----------
    row: pd.DataFrame row

    url_col: str
        url_column

    Returns
    -------
    content_length: int
    """
    if row[url_col] is not None:
        url = row[url_col]
    else:
        url = row.download_url
    if url.startswith("ftp."):
        url = "ftp://" + url
    try:
        r = requests_3_retries().head(url)
        size = int(r.headers["content-length"])
        r.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(f"Connection to {url} has timed out. Please retry.")
    except requests.exceptions.HTTPError:
        print(
            f"The download URL:  {url}  is likely invalid.\n"
            f"Removing {row.run_accession} from the download list\n",
            flush=True,
        )
        return np.NaN
    except KeyError:
        print("Key error for: " + url, flush=True)
        return 0
    return size


def md5_validate_file(file_path, md5_hash):
    """Check file containt against an MD5.

    Parameters
    ----------
    file_path: string
               Path to file
    md5_hash: string
             Expected md5 hash

    Returns
    -------
    valid: bool
           True if expected and observed md5 match
    """
    observed_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            # read 1MB
            chunk = f.read(1000 * 1000)
            if not chunk:
                break
            observed_md5.update(chunk)
    return observed_md5.hexdigest() == md5_hash


def download_file(
    url,
    file_path,
    md5_hash=None,
    timeout=10,
    block_size=1024 * 1024,
    show_progress=False,
):
    """Resumable download.
    Expect the server to support byte ranges.

    Parameters
    ----------
    url: string
         URL
    file_path: string
               Local file path to store the downloaded file
    md5_hash: string
              Expected MD5 string of downloaded file
    timeout: int
             Seconds to wait before terminating request
    block_size: int
                Chunkx of bytes to read (default: 1024 * 1024 = 1MB)
    show_progress: bool
                   Show progress bar
    """
    if url.startswith("ftp."):
        url = "ftp://" + url
        session = requests.Session()
    else:
        session = requests
    if os.path.exists(file_path) and os.path.getsize(file_path):
        return
    tmp_file_path = file_path + ".part"
    first_byte = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
    file_mode = "ab" if first_byte else "wb"
    file_size = -1
    try:
        file_size = int(session.head(url).headers["Content-length"])
        headers = {"Range": "bytes=%s-" % first_byte}
        r = session.get(url, headers=headers, stream=True)
        if show_progress:
            desc = "Downloading {}".format(url.split("/")[-1])
            pbar = tqdm(
                total=file_size,
                initial=first_byte,
                unit="B",
                unit_scale=True,
                desc=desc,
            )
        with open(tmp_file_path, file_mode) as f:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    if show_progress:
                        pbar.update(block_size)
        if show_progress:
            pbar.close()
    except IOError as e:
        sys.stderr.write("IO Error - {}\n".format(e))
    finally:
        # Move the temp file to desired location
        if file_size == os.path.getsize(tmp_file_path):
            # if there's a hash value, validate the file
            if md5_hash and not md5_validate_file(tmp_file_path, md5_hash):
                raise Exception("Error validating the file against its MD5 hash")
            shutil.move(tmp_file_path, file_path)
        elif file_size == -1:
            raise Exception("Error getting Content-Length from server: %s" % url)

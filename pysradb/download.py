import math
import os
import hashlib
import requests
import shutil
import sys

import numpy as np
from tqdm.autonotebook import tqdm

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


def get_file_size(row):
    """Get size of file to be downloaded.

    Parameters
    ----------
    row: pd.DataFrame row

    Returns
    -------
    content_length: int
    """
    if row.srapath_url is not None:
        url = row.srapath_url
    else:
        url = row.download_url
    return float(requests.head(url).headers["content-length"])


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
    show_progress=True,
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
    if os.path.exists(file_path) and os.path.getsize(file_path):
        return
    tmp_file_path = file_path + ".part"
    first_byte = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
    file_mode = "ab" if first_byte else "wb"
    file_size = -1
    try:
        file_size = int(requests.head(url).headers["Content-length"])
        headers = {"Range": "bytes=%s-" % first_byte}
        r = requests.get(url, headers=headers, stream=True)
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

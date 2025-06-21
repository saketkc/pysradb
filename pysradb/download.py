import hashlib
import math
import os
import shutil
import sys
import warnings

import numpy as np
import requests
from tqdm import tqdm

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
    import requests
    import numpy as np
    import sys
    if row[url_col] is not None:
        url = row[url_col]
    else:
        url = row.download_url
    if url is None or url is np.nan:
        return 0
    if not isinstance(url, str):
        return 0
    if url.startswith("ftp."):
        url = "ftp://" + url
    try:
        r = requests.head(url)
        size = int(r.headers["content-length"])
        r.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(f"Connection to {url} has timed out. Please retry.")
    except requests.exceptions.HTTPError:
        print(
            f"The download URL:  {url}  is likely invalid.\n"
            f"Removing {getattr(row, 'run_accession', '')} from the download list\n",
            flush=True,
        )
        return np.NaN
    except KeyError:
        print("Key error for: " + url, flush=True)
        return 0
    return size

def md5_validate_file(file_path, md5_hash):
    """Check file content against an MD5.

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
        for chunk in iter(lambda: f.read(1000 * 1000), b""):
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
                Chunk of bytes to read (default: 1024 * 1024 = 1MB)
    show_progress: bool
                   Show progress bar
    """
    if os.path.exists(file_path) and os.path.getsize(file_path):
        return
    tmp_file_path = file_path + ".part"
    first_byte = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
    file_mode = "ab" if first_byte else "wb"
    headers = {"Range": f"bytes={first_byte}-"} if first_byte else None

    try:
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            # Fallback to 0 if Content-Length is missing
            file_size = int(r.headers.get("Content-Length", 0))
            if show_progress:
                desc = f"Downloading {os.path.basename(file_path)}"
                pbar = tqdm(total=file_size, initial=first_byte, unit="B", unit_scale=True, desc=desc)
            with open(tmp_file_path, file_mode) as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        if show_progress:
                            pbar.update(len(chunk))
            if show_progress:
                pbar.close()
    except IOError as e:
        sys.stderr.write(f"IO Error - {e}\n")
        raise

    # Move the temp file to desired location
    if os.path.exists(tmp_file_path):
        if md5_hash and not md5_validate_file(tmp_file_path, md5_hash):
            raise Exception("Error validating the file against its MD5 hash")
        shutil.move(tmp_file_path, file_path)
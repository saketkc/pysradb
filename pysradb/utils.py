import errno
import gzip
import io
import ntpath
import os
import shlex
import subprocess
import urllib.request as urllib_request
import warnings

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm.autonotebook import tqdm

from .exceptions import IncorrectFieldException

warnings.simplefilter(action="ignore", category=FutureWarning)


tqdm.pandas()


def path_leaf(path):
    """Get path's tail from a filepath.

    Parameters
    ----------
    path: string
          Filepath

    Returns
    -------
    tail: string
          Filename
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def requests_3_retries():
    """Generates a requests session object that allows 3 retries.

    Returns
    -------
    session: requests.Session
        requests session object that allows 3 retries for server-side
        errors.
    """
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def scientific_name_to_taxid(name):
    """Converts a scientific name to its corresponding taxonomy ID.

    Parameters
    ----------
    name: str
        Scientific name of interest.

    Returns
    -------
    taxid: str
        Taxonomy Id of the Scientific name.

    Raises
    ------
    IncorrectFieldException
        If the scientific name cannot be found.

    """

    r = requests.get(
        "https://www.ebi.ac.uk/ena/data/taxonomy/v1/taxon/scientific-name/" + name,
        timeout=5,
    )
    if r.status_code == 404:
        raise IncorrectFieldException(f"Unknown scientific name: {name}")
    r.raise_for_status()
    return r.json()[0]["taxId"]


def unique(sequence):
    """Get unique elements from a list maintaining the order.

    Parameters
    ----------
    input_list: list

    Returns
    -------
    unique_list: list
                 List with unique elements maintaining the order
    """
    visited = set()
    return [x for x in sequence if not (x in visited or visited.add(x))]


class TqdmUpTo(tqdm):
    """Alternative Class-based version of the above.
    Provides `update_to(n)` which uses `tqdm.update(delta_n)`.
    Inspired by [twine#242](https://github.com/pypa/twine/pull/242),
    [here](https://github.com/pypa/twine/commit/42e55e06).

    Credits:
    https://github.com/tqdm/tqdm/blob/69326b718905816bb827e0e66c5508c9c04bc06c/examples/tqdm_wget.py
    """

    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize


def _extract_first_field(data):
    """Extract first field from a list of fields."""
    return list(next(iter(zip(*data))))


def _find_aspera_keypath(aspera_dir=None):
    """Locate aspera key.

    Parameters
    ----------
    aspera_dir: string
                Location to aspera directory (optional)

    Returns
    -------
    aspera_keypath: string
                    Location to aspera key
    """
    if aspera_dir is None:
        aspera_dir = os.path.join(os.path.expanduser("~"), ".aspera")
    aspera_keypath = os.path.join(
        aspera_dir, "connect", "etc", "asperaweb_id_dsa.openssh"
    )
    if os.path.isfile(aspera_keypath):
        return aspera_keypath


def mkdir_p(path):
    """Python version mkdir -p

    Parameters
    ----------
    path : string
           Path to directory to create
    """
    if path:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def order_dataframe(df, columns):
    """Order a dataframe

    Order a dataframe by moving the `columns` in the front

    Parameters
    ----------
    df: Dataframe
        Dataframe
    columns: list
             List of columns that need to be put in front
    """
    remaining_columns = [w for w in df.columns if w not in columns]
    df = df[columns + remaining_columns]
    return df


def _get_url(url, download_to, show_progress=True):
    """Download anything at a given url.

    Parameters
    ----------
    url: string
         http/https/ftp url
    download_to: string
                 File location to write the downloaded file to
    show_progress: bool
                   Set to True by default to print progress bar
    """
    desc_file = "Downloading {}".format(url.split("/")[-1])
    mkdir_p(os.path.dirname(download_to))
    if show_progress:
        with TqdmUpTo(
            unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=desc_file
        ) as t:
            urllib_request.urlretrieve(
                url, download_to, reporthook=t.update_to, data=None
            )
    else:
        urllib_request.urlretrieve(url, download_to)


def run_command(command, verbose=False):
    """Run a shell command"""
    process = subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    while True:
        output = process.stdout.readline().strip()
        output = output.decode("utf-8")
        if output == "" and process.poll() is not None:
            break
        if output:
            if verbose:
                print((str(output.strip())))
    rc = process.poll()
    return rc


def get_gzip_uncompressed_size(filepath):
    """Get uncompressed size of a .gz file

    Parameters
    ----------
    filepath: string
              Path to input file

    Returns
    -------
    filesize: int
              Uncompressed file size
    """
    with gzip.open(filepath, "rb") as file_obj:
        return file_obj.seek(0, io.SEEK_END)


def confirm(preceeding_text):
    """Confirm user input.

    Parameters
    ----------
    preceeding_text: str
                     Text to print

    Returns
    -------
    response: bool
    """
    print(os.linesep, flush=True)
    notification_str = "Please respond with 'y' or 'n'"
    while True:
        choice = input("{} [Y/n]: ".format(preceeding_text)).lower()
        if choice in ["yes", "y"] or not choice:
            return True
        if choice in ["no", "n"]:
            return False
        print(notification_str, flush=True)


def copyfileobj(fsrc, fdst, bufsize=16384, filesize=None, desc=""):
    """Copy file object with a progress bar.

    Parameters
    ----------
    fsrc: filehandle
          Input file handle
    fdst: filehandle
          Output file handle
    bufsize: int
             Length of output buffer
    filesize: int
              Input file file size
    desc: string
          Description for tqdm status
    """
    with tqdm(
        total=filesize,
        unit="B",
        unit_scale=True,
        miniters=1,
        unit_divisor=1024,
        desc=desc,
    ) as pbar:
        while True:
            buf = fsrc.read(bufsize)
            if not buf:
                break
            fdst.write(buf)
            pbar.update(len(buf))

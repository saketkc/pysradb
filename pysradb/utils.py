import errno
import os
import shlex
import sys
import subprocess
from tqdm import tqdm
PY3 = True
if sys.version_info[0] < 3:
    PY3 = False


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
    return list(next(zip(*data)))


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
        aspera_dir = os.path.join(os.path.expanduser('~'), '.aspera')
    aspera_keypath = os.path.join(aspera_dir, 'connect', 'etc',
                                  'asperaweb_id_dsa.openssh')
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
    if PY3:
        import urllib.request as urllib_request
    else:
        import urllib as urllib_request
    desc_file = url.split('/')[-1]
    if show_progress:
        with TqdmUpTo(
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                desc=desc_file) as t:
            urllib_request.urlretrieve(
                url, download_to, reporthook=t.update_to, data=None)
    else:
        urllib_request.urlretrieve(url, download_to)


def run_command(command, verbose=False):
    """Run a shell command"""
    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf8')
    while True:
        output = str(process.stdout.readline().strip())
        if output == '' and process.poll() is not None:
            break
        if output:
            if verbose:
                print(str(output.strip()))
    rc = process.poll()
    return rc

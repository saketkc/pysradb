"""Utilities to interact with GEO online"""

import gzip
import os
import re
import sys
from io import StringIO

import pandas as pd
import requests
from lxml import html

from .download import download_file
from .utils import _get_url, copyfileobj, get_gzip_uncompressed_size

PY3 = True
if sys.version_info[0] < 3:
    PY3 = False


class GEOweb(object):
    def __init__(self, verbose=True):
        """Initialize GEOweb without any database.

        Parameters
        ----------
        verbose: bool
                 Print file download information. Default True.
        """
        self.verbose = verbose

    def get_download_links(self, gse):
        """Obtain all links from the GEO FTP page.

        Parameters
        ----------
        gse: string
             GSE ID

        Returns
        -------
        links: list
               List of all valid downloadable links present for a GEO ID
        """
        prefix = gse[:-3]
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}nnn/{gse}/suppl/"
        link_objects = html.fromstring(requests.get(url).content).xpath("//a")
        links = [i.attrib["href"] for i in link_objects]
        # remove vulnerability link
        links = [
            link
            for link in links
            if link != "https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
        ]
        # Check if returned results are a valid page - a link to the
        # home page only exists where the GSE ID dow not exist
        if "/" in links:
            raise KeyError(f"The provided GEO ID {gse} does not exist.")

        # The list of links for a valid GSE ID also contains a link to
        # the parent directory - we do not want that
        links = [i for i in links if "geo/series/" not in i]

        # The links are relative, we need absolute links to download
        links = [i for i in links]

        return links, url

    def download(self, links, root_url, gse, verbose=False, out_dir=None):
        """Download GEO files.

        Parameters
        ----------
        links: list
               List of all links valid downloadable present for a GEO ID
        root_url: string
                  url for root directory for a GEO ID
        gse: string
             GEO ID
        verbose: bool
                 Print file list
        out_dir: string
                 Directory location for download
        """
        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads")

        # store output in a separate directory
        out_dir = os.path.join(out_dir, gse)
        os.makedirs(out_dir, exist_ok=True)

        # Display files to be downloaded
        if verbose:
            print("\nThe following files will be downloaded: \n")
            for link in links:
                print(link)
            print(os.linesep)
        # Check if we can access list of files in the tar file
        tar_list = [i for i in links if ".tar" in i]
        if "filelist.txt" in links:
            tar_file = tar_list[0]
            if verbose:
                print(f"\nThe tar file {tar_file} contains the following files:\n")
                file_list_contents = requests.get(
                    root_url + "filelist.txt"
                ).content.decode("utf-8")
                print(file_list_contents)

        # Download files
        for link in links:
            # add a prefix to distinguish filelist.txt from different downloads
            prefix = ""
            if link == "filelist.txt":
                prefix = gse + "_"
            geo_path = os.path.join(out_dir, prefix + link)
            download_file(root_url + link, geo_path, show_progress=True)


def download_geo_matrix(accession, output_dir="."):
    """
    Download a GEO Matrix file for a given GEO accession ID.

    Args:
        accession (str): GEO accession ID (e.g., 'GSE234190').
        output_dir (str): Directory to save the downloaded file (default: current directory).

    Returns:
        str: Path to the downloaded file.

    Raises:
        Exception: If the download fails.
    """
    # Construct the URL for the GEO Matrix file
    url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{accession[:-3]}nnn/{accession}/matrix/{accession}_series_matrix.txt.gz"

    # Define the output file path
    output_file = os.path.join(output_dir, f"{accession}_series_matrix.txt.gz")

    # Download the file using _get_url
    try:
        _get_url(url, output_file)
        return output_file
    except Exception as e:
        raise Exception(
            f"Failed to download GEO Matrix file for {accession}. Exception: {str(e)}"
        )


def parse_geo_matrix_to_tsv(input_file, output_file):
    """
    Parse a GEO Matrix file to a TSV file, extracting the expression data.

    Args:
        input_file (str): Path to the input GEO Matrix file (gzipped).
        output_file (str): Path to save the output TSV file.

    Returns:
        pandas.DataFrame: The parsed expression data.
    """
    # Read the gzipped file and extract the data section
    data_lines = []
    data_section = False

    with gzip.open(input_file, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "!series_matrix_table_begin":
                data_section = True
                continue
            elif line == "!series_matrix_table_end":
                break
            if data_section and line:
                data_lines.append(line)

    # Use pandas.read_csv to parse the data section
    df = pd.read_csv(StringIO("\n".join(data_lines)), sep="\t", comment="!")

    # Save to TSV
    df.to_csv(output_file, sep="\t", index=False)

    return df

"""Utilities to interact with GEO online"""

import gzip
import os
import re
import requests
import sys
from lxml import html

from .download import download_file
from .geodb import GEOdb
from .utils import _get_url
from .utils import copyfileobj
from .utils import get_gzip_uncompressed_size

PY3 = True
if sys.version_info[0] < 3:
    PY3 = False


class GEOweb(GEOdb):
    def __init__(self):
        """Initialize GEOweb without any database."""

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
            download_file(
                root_url.lstrip("https://") + link, geo_path, show_progress=True
            )

    def download_matrix(self, gse, out_dir=None, verbose=False):

        prefix = gse[:-3]
        # FTP URL pattern for matrix files:
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}nnn/{gse}/matrix/"

        try:
            page = requests.get(url)
            tree = html.fromstring(page.content)
        except Exception as e:
            raise Exception(f"Error accessing {url}: {e}")

        # Extract links containing "series_matrix" (typically our target file)
        link_objects = tree.xpath("//a")
        links = [link.attrib["href"] for link in link_objects if "series_matrix" in link.attrib.get("href", "")]

        if not links:
            raise Exception(f"No matrix files found for {gse} at {url}")

        # Select the first matching matrix file link.
        matrix_file = links[0]
        file_url = url + matrix_file

        if out_dir in (None, "."):
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads")
        out_dir = os.path.join(out_dir, gse)
        os.makedirs(out_dir, exist_ok=True)

        matrix_path = os.path.join(out_dir, matrix_file)

        # Download the file using the existing download_file utility.
        download_file(file_url, matrix_path, show_progress=True)

        if verbose:
            print(f"Downloaded matrix file from {file_url} to {matrix_path}")

        return matrix_path

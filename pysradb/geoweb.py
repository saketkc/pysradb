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
from .utils import mkdir_p

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

    def get_matrix_links(self, gse):
        """Obtain links to matrix files from the GEO FTP matrix directory.

        Parameters
        ----------
        gse: string
             GSE ID

        Returns
        -------
        links: list
               List of all valid matrix file links present for a GEO ID
        url: string
             URL of the matrix directory
        """
        prefix = gse[:-3]
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}nnn/{gse}/matrix/"

        try:
            response = requests.get(url)
            response.raise_for_status()
            link_objects = html.fromstring(response.content).xpath("//a")
            links = [i.attrib["href"] for i in link_objects]

            # Remove vulnerability link and parent directory link
            links = [
                link
                for link in links
                if link != "https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
                and "geo/series/" not in link
                and link != "/"
            ]

            # Filter for matrix files (typically .txt.gz)
            matrix_files = [link for link in links if "_series_matrix.txt.gz" in link]

            if not matrix_files:
                print(f"No matrix files found for {gse}")

            return matrix_files, url

        except requests.exceptions.HTTPError:
            print(f"No matrix directory found for {gse}")
            return [], None

    def download_matrix(self, gse, out_dir=None):
        """Download matrix files for a GEO accession.

        Parameters
        ----------
        gse: string
             GSE ID
        out_dir: string, optional
                 Directory location for download

        Returns
        -------
        downloaded_files: list
                         Paths to downloaded matrix files
        """
        matrix_files, matrix_url = self.get_matrix_links(gse)

        if not matrix_files:
            return []

        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads", gse, "matrix")

        mkdir_p(out_dir)

        downloaded_files = []

        print("\nThe following matrix files will be downloaded: \n")
        for link in matrix_files:
            print(link)
        print(os.linesep)

        for link in matrix_files:
            file_path = os.path.join(out_dir, link)
            download_file(
                matrix_url.lstrip("https://") + link,
                file_path,
                show_progress=True
            )
            downloaded_files.append(file_path)

        return downloaded_files

    def download(self, links, root_url, gse, verbose=False, out_dir=None, matrix_only=False):
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
        matrix_only: bool
                    If True, only download matrix files
        """
        if matrix_only:
            return self.download_matrix(gse, out_dir)

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

"""Utilities to interact with GEO online"""

import gzip
import os
import re
import requests
import sys
from lxml import html
import shutil
import pandas as pd
from io import StringIO

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

    # ------------- GEO Matrix Feature Start -------------
    def get_matrix_links(self, gse):
        """
        Obtain matrix file links from the GEO FTP matrix folder for a GSE accession.
        """
        prefix = gse[:-3]
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}nnn/{gse}/matrix/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            link_objects = html.fromstring(response.content).xpath("//a")
            links = [i.attrib["href"] for i in link_objects]
            # Filter for matrix files - usually .txt or .gz
            matrix_links = [
                link for link in links if link.endswith(".txt") or link.endswith(".gz")
            ]
            return matrix_links, url
        except Exception as e:
            print(f"Error fetching matrix links: {e}")
            return [], url

    def download_geo_matrix(self, accession, out_dir=None, to_tsv=False, out_tsv=None):
        """
        Download GEO matrix files and optionally convert to TSV.
        """
        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads")
        out_dir = os.path.join(out_dir, accession)
        os.makedirs(out_dir, exist_ok=True)

        matrix_links, root_url = self.get_matrix_links(accession)
        if not matrix_links:
            print("No matrix files found for this accession.")
            return

        for matrix_file in matrix_links:
            matrix_url = root_url + matrix_file
            dest_path = os.path.join(out_dir, matrix_file)
            print(f"Downloading {matrix_url} -> {dest_path}")
            # Download the file
            with requests.get(matrix_url, stream=True) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            print(f"Downloaded: {dest_path}")

            # If --to-tsv is enabled, parse and convert
            if to_tsv:
                tsv_path = (
                    out_tsv if out_tsv else os.path.splitext(dest_path)[0] + ".tsv"
                )
                self.convert_geo_matrix_to_tsv(dest_path, tsv_path)
                print(f"Converted matrix to TSV: {tsv_path}")

    def convert_geo_matrix_to_tsv(self, input_path, output_path):
        """
        Convert a GEO matrix file (.txt or .gz) to TSV by skipping lines starting with '!'
        """
        # Handle .gz files
        open_func = gzip.open if input_path.endswith(".gz") else open
        with open_func(input_path, "rt") as infile, open(output_path, "w") as outfile:
            for line in infile:
                if not line.startswith("!"):
                    outfile.write(line)

    # ------------- GEO Matrix Feature End -------------

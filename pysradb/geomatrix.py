"""Utilities to interact with GEO Matrix files"""

import gzip
import os
import pandas as pd
import re
import requests
import sys
from lxml import html

from .download import download_file
from .geoweb import GEOweb
from .utils import mkdir_p


class GEOMatrix:
    """Class to handle GEO Matrix files.

    This class provides methods to download and parse GEO Matrix files,
    which contain processed expression data.

    Attributes
    ----------
    gse : str
        GEO Series accession ID (e.g., GSE234190)
    """

    def __init__(self, gse):
        """Initialize GEOMatrix with a GEO accession.

        Parameters
        ----------
        gse : str
            GEO Series accession ID (e.g., GSE234190)
        """
        self.gse = gse
        self.geoweb = GEOweb()
        self.matrix_files = []
        self.matrix_url = None
        self.matrix_path = None
        self.metadata = {}
        self.data = None

    def get_matrix_links(self):
        """Get links to matrix files for a GEO accession.

        Returns
        -------
        list
            List of matrix file links
        str
            URL of the matrix directory
        """
        prefix = self.gse[:-3]
        matrix_url = (
            f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}nnn/{self.gse}/matrix/"
        )

        try:
            response = requests.get(matrix_url)
            response.raise_for_status()
            link_objects = html.fromstring(response.content).xpath("//a")
            links = [i.attrib["href"] for i in link_objects]

            # Remove vulnerability link and parent directory link
            links = [
                link
                for link in links
                if link
                != "https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
                and "geo/series/" not in link
                and link != "/"
            ]

            # Filter for matrix files (typically .txt.gz)
            matrix_files = [link for link in links if "_series_matrix.txt.gz" in link]

            if not matrix_files:
                print(f"No matrix files found for {self.gse}")

            self.matrix_files = matrix_files
            self.matrix_url = matrix_url

            return matrix_files, matrix_url

        except requests.exceptions.HTTPError:
            print(f"No matrix directory found for {self.gse}")
            return [], None

    def download_matrix(self, out_dir=None):
        """Download matrix files for a GEO accession.

        Parameters
        ----------
        out_dir : str, optional
            Directory to save downloaded files, by default None
            which uses ./pysradb_downloads/{gse}/matrix/

        Returns
        -------
        list
            Paths to downloaded matrix files
        """
        if not self.matrix_files:
            self.get_matrix_links()

        if not self.matrix_files:
            return []

        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads", self.gse, "matrix")

        mkdir_p(out_dir)

        downloaded_files = []

        print("\nThe following matrix files will be downloaded: \n")
        for link in self.matrix_files:
            print(link)
        print(os.linesep)

        for link in self.matrix_files:
            file_path = os.path.join(out_dir, link)
            download_file(
                self.matrix_url.lstrip("https://") + link, file_path, show_progress=True
            )
            downloaded_files.append(file_path)
            self.matrix_path = file_path

        return downloaded_files

    def parse_matrix(self, matrix_file=None):
        """Parse a GEO matrix file.

        Parameters
        ----------
        matrix_file : str, optional
            Path to matrix file, by default None which uses the last downloaded file

        Returns
        -------
        dict
            Metadata extracted from the matrix file
        pandas.DataFrame
            Data extracted from the matrix file
        """
        if matrix_file is None:
            matrix_file = self.matrix_path

        if matrix_file is None:
            raise ValueError("No matrix file specified or downloaded")

        # Check if the file is gzipped
        if matrix_file.endswith(".gz"):
            open_func = gzip.open
            mode = "rt"
        else:
            open_func = open
            mode = "r"

        # Read the file
        metadata_lines = []
        data_lines = []
        metadata_section = True

        with open_func(matrix_file, mode) as f:
            for line in f:
                if line.startswith("!"):
                    metadata_lines.append(line.strip())
                else:
                    if metadata_section:
                        metadata_section = False
                    data_lines.append(line)

        # Parse metadata
        metadata = {}
        for line in metadata_lines:
            if ":" in line:
                key, value = line[1:].split(":", 1)
                metadata[key.strip()] = value.strip()

        # Parse data
        data = pd.read_csv(
            pd.io.common.StringIO("".join(data_lines)), sep="\t", index_col=0
        )

        self.metadata = metadata
        self.data = data

        return metadata, data

    def to_dataframe(self, matrix_file=None):
        """Convert a GEO matrix file to a pandas DataFrame.

        Parameters
        ----------
        matrix_file : str, optional
            Path to matrix file, by default None which uses the last downloaded file

        Returns
        -------
        pandas.DataFrame
            Data extracted from the matrix file
        """
        if self.data is None:
            self.parse_matrix(matrix_file)

        return self.data

    def to_tsv(self, output_file, matrix_file=None):
        """Convert a GEO matrix file to a TSV file.

        Parameters
        ----------
        output_file : str
            Path to output TSV file
        matrix_file : str, optional
            Path to matrix file, by default None which uses the last downloaded file

        Returns
        -------
        str
            Path to output TSV file
        """
        if self.data is None:
            self.parse_matrix(matrix_file)

        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            mkdir_p(output_dir)

        # Write to TSV
        self.data.to_csv(output_file, sep="\t")

        return output_file

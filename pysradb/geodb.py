"""Methods to interact with SRA"""

# This is now defunct and will be removed in a future release.

import gzip
import os
import re
import sys
from io import StringIO

import pandas as pd

from .basedb import BASEdb
from .utils import _get_url, copyfileobj, get_gzip_uncompressed_size

PY3 = True
if sys.version_info[0] < 3:
    PY3 = False

GEOmetadb_URL = "http://starbuck1.s3.amazonaws.com/sradb/GEOmetadb.sqlite.gz"


def download_geodb_file(download_dir=os.getcwd(), overwrite=True):
    """Download GEOmetadb.sqlite file.

    Parameters
    ----------
    download_dir: string
                  Directory to download SRAmetadb.sqlite
    overwrite: bool
               overwrite existing file(s).
               Set to True by default.

    """
    download_location = os.path.join(download_dir, "GEOmetadb.sqlite.gz")
    download_location_unzip = download_location.rstrip(".gz")

    if os.path.isfile(download_location) and overwrite is False:
        raise RuntimeError(
            "{} already exists! Set `overwrite=True` to redownload.".format(
                download_location
            )
        )
    if os.path.isfile(download_location_unzip) and overwrite is False:
        raise RuntimeError(
            "{} already exists! Set `overwrite=True` to redownload.".format(
                download_location_unzip
            )
        )

    try:
        _get_url(GEOmetadb_URL, download_location)
    except Exception as e:
        raise RuntimeError(
            "Could not use {}.\nException: {}.\n".format(GEOmetadb_URL, e)
        )
    print("Extracting {} ...".format(download_location))
    filesize = get_gzip_uncompressed_size(download_location)
    with gzip.open(download_location, "rb") as fh_in:
        with open(download_location_unzip, "wb") as fh_out:
            copyfileobj(
                fh_in,
                fh_out,
                filesize=filesize,
                desc="Extracting {}".format("GEOmetadb.sqlite.gz"),
            )
    print("Done!")
    db = GEOdb(download_location_unzip)
    metadata = db.query("SELECT * FROM metaInfo")
    db.close()
    print("Metadata associated with {}:".format(download_location_unzip))
    print(metadata)


class GEOdb(BASEdb):
    def __init__(self, sqlite_file):
        """Initialize SRAdb.

        Parameters
        ----------

        sqlite_file: string
                     Path to unzipped SRAmetadb.sqlite file


        """
        super(GEOdb, self).__init__(sqlite_file)
        self._db_type = "GEO"
        self.valid_in_type = ["GSE", "GPL", "GSM", "GDS"]

    def gse_metadata(self, gse):
        """Get metadata for GSE ID.

        Parameters
        ----------
        gse: string
             GSE ID

        Returns
        -------
        metadata_df: DataFrame
                     A dataframe with relevant fields
        """
        return self.query("SELECT * from gse WHERE gse='{}';".format(gse))

    def gsm_metadata(self, gsm):
        """Get metadata for GSM ID.

        Parameters
        ----------
        gsm: string
             GSM ID

        Returns
        -------
        metadata_df: DataFrame
                     A dataframe with relevant fields
        """
        return self.query("SELECT * from gsm WHERE gsm='{}';".format(gsm))

    def geo_convert(self, from_acc):
        """Convert one GEO accession to other.

        Parameters
        ----------
        from_acc: string
                  GPL/GSE/GSM accession ID

        Returns
        -------
        mapping_df: DataFrame
                    A dataframe with relevant mappings
        """
        return self.query(
            "SELECT * FROM geoConvert WHERE from_acc='{}';".format(from_acc)
        )

    def gse_to_gsm(self, gse):
        """Fetch GSMs for a GSE.

        Parameters
        ----------
        gse: string
             GSE ID

        Returns
        -------
        mapping_df: DataFrame
                    A dataframe with relevant mappings
        """
        return self.query("SELECT * FROM gse_gsm WHERE gse='{}'".format(gse))

    def gsm_to_gse(self, gsm):
        """Fetch GSE for a GSM.

        Parameters
        ----------
        gsm: string
             GSM ID

        Returns
        -------
        mapping_df: DataFrame
                    A dataframe with relevant mappings
        """
        mapping_df = self.query("SELECT * FROM gse_gsm WHERE gsm='{}'".format(gsm))
        return mapping_df.loc[:, ["gsm", "gse"]]

    def guess_srp_from_gse(self, gse):
        """Convert GSE to SRP id.

        Parameters
        ----------
        gse: string
             GSE ID

        Returns
        -------
        srp: string
             SRP ID
        """
        results = self.query('SELECT * FROM gse WHERE gse = "' + gse + '"')
        if results.shape[0] == 1:
            supp_file = results["supplementary_file"][0]
            if supp_file:
                splitted = supp_file.split(";")
                if len(splitted):
                    match = re.findall("SRP.*", splitted[-1])
                    if len(match):
                        srp = match[0].split("/")[-1]
                        return srp
        return None


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

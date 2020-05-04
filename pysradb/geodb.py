"""Methods to interact with SRA"""

import gzip
import os
import re
import sys

from .basedb import BASEdb
from .utils import _get_url
from .utils import copyfileobj
from .utils import get_gzip_uncompressed_size

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
            "{} already exists! Set `overwrite=True` to redownload.".forma(
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

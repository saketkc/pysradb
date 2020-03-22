"""Methods to interact with SRA"""

import gzip
import os
import re
import subprocess
import sys

from subprocess import PIPE

import numpy as np
import pandas as pd
from tqdm.autonotebook import tqdm

tqdm.pandas()

from .basedb import BASEdb

from .filter_attrs import expand_sample_attribute_columns

from .utils import confirm
from .utils import _find_aspera_keypath
from .utils import _get_url
from .utils import get_gzip_uncompressed_size
from .utils import copyfileobj
from .utils import mkdir_p
from .utils import order_dataframe
from .utils import run_command
from .utils import unique

from .download import download_file
from .download import get_file_size
from .download import millify

from .taxid2name import TAXID_TO_NAME
from .utils import path_leaf

FTP_PREFIX = {
    "fasp": "anonftp@ftp-trace.ncbi.nlm.nih.gov:",
    "ftp": "ftp://ftp-trace.ncbi.nlm.nih.gov",
}
SRADB_URL = [
    "https://s3.amazonaws.com/starbuck1/sradb/SRAmetadb.sqlite.gz",
    "https://gbnci-abcc.ncifcrf.gov/backup/SRAmetadb.sqlite.gz",
]

ASCP_CMD_PREFIX = "ascp -k 1 -QT -l 2000m -i"
PY3_VERSION = sys.version_info.minor


def _create_query(select_type_sql, gses):
    sql = (
        "SELECT DISTINCT "
        + select_type_sql
        + " FROM sra_ft WHERE sra_ft MATCH '"
        + " OR ".join(gses)
        + "';"
    )
    return sql


def _expand_sample_attrs(metadata_df):
    if "sample_attribute" in metadata_df.columns.tolist():
        metadata_df = expand_sample_attribute_columns(metadata_df)
        metadata_df = metadata_df.drop(columns=["sample_attribute"])
    return metadata_df


def _listify(ids):
    """convert string to list of unit length"""
    if isinstance(ids, str):
        ids = [ids]
    return ids


def _prettify_df(df, out_type, expand_sample_attributes):
    if len(df.index):
        df = df[out_type].sort_values(by=out_type)
    if expand_sample_attributes:
        df = _expand_sample_attrs(df)
    return df


def download_sradb_file(download_dir=os.getcwd(), overwrite=True, keep_gz=False):
    """Download SRAdb.sqlite file.

    Parameters
    ----------
    download_dir: string
                  Directory to download SRAmetadb.sqlite
    overwrite: bool
               overwrite existing file(s).
               Set to True by default.
    keep_gz: bool
             Delete .gz file after extraction is complete

    """
    download_location = os.path.join(download_dir, "SRAmetadb.sqlite.gz")
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
    if os.path.isfile(download_location_unzip):
        os.remove(download_location_unzip)
    if os.path.isfile(download_location):
        os.remove(download_location)
    try:
        _get_url(SRADB_URL[0], download_location)
    except Exception as e:
        # Try other URL
        sys.stderr.write(
            "Could not use {}.\nException: {}.\nTrying alternate url ...\n".format(
                SRADB_URL[0], e
            )
        )
        _get_url(SRADB_URL[1], download_location)
    print("Extracting {} ...".format(download_location))
    filesize = get_gzip_uncompressed_size(download_location)
    with gzip.open(download_location, "rb") as fh_in:
        with open(download_location_unzip, "wb") as fh_out:
            copyfileobj(
                fh_in,
                fh_out,
                filesize=filesize,
                desc="Extracting {}".format("SRAmetadb.sqlite.gz"),
            )
    if not keep_gz:
        if os.path.isfile(download_location):
            os.remove(download_location)
    print("Done!")
    db = SRAdb(download_location_unzip)
    metadata = db.query("SELECT * FROM metaInfo")
    db.close()
    print("Metadata associated with {}:".format(download_location_unzip))
    print(metadata)


def _verify_srametadb(filepath):
    """Check if supplied SQLite is valid"""
    try:
        db = BASEdb(filepath)
    except:
        print(
            "{} not a valid SRAmetadb.sqlite file or path.\n".format(filepath)
            + "Please download one using `pysradb metadb`."
        )
        sys.exit(1)
    metadata = db.query("SELECT * FROM metaInfo")
    db.close()
    if list(metadata.iloc[0].values) != ["schema version", "1.0"]:
        print(
            "{} not a valid SRAmetadb.sqlite file.\n".format(filepath)
            + "Please download one using `pysradb metadb`."
        )
        sys.exit(1)


class SRAdb(BASEdb):
    def __init__(self, sqlite_file):
        """Initialize SRAdb.

        Parameters
        ----------

        sqlite_file: string
                     Path to unzipped SRAmetadb.sqlite file


        """
        _verify_srametadb(sqlite_file)
        super(SRAdb, self).__init__(sqlite_file)
        self._db_type = "SRA"
        self.valid_in_acc_type = [
            "SRA",
            "ERA",
            "DRA",
            "SRP",
            "ERP",
            "DRP",
            "SRS",
            "ERS",
            "DRS",
            "SRX",
            "ERX",
            "DRX",
            "SRR",
            "ERR",
            "DRR",
        ]
        self.valid_in_type = {
            "SRA": "submission",
            "ERA": "submission",
            "DRA": "submission",
            "SRP": "study",
            "ERP": "study",
            "DRP": "study",
            "SRS": "sample",
            "ERS": "sample",
            "DRS": "sample",
            "SRX": "experiment",
            "ERX": "experiment",
            "DRX": "experiment",
            "SRR": "run",
            "ERR": "run",
            "DRR": "run",
        }

    def sra_metadata(
        self,
        acc,
        out_type=[
            "study_accession",
            "experiment_accession",
            "sample_accession",
            "run_accession",
        ],
        assay=False,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
        output_read_lengths=False,
        acc_is_searchstr=False,
    ):
        """Get metadata for the provided SRA accession.

        Parameters
        ----------
        acc: string or list
             SRA accession ID
        out_type: list
                  List of columns to output
        assay: bool
               True if assay should be outputted
        sample_attribute: bool
                          True if sample_attribute should be outputted
        detailed: bool
                  True if full metadata tables should be outputted
        expand_sample_attributes: bool
                                  Should sample_attribute column be expanded?
        output_read_lengths: bool
                             True if read lengths should be calculated
        acc_is_searchstr: bool
                          True if acc is a search string


        Returns
        -------
        metadata_df: DataFrame
                     A dataframe with all relevant columns
        """
        if not isinstance(acc, list):
            acc = [acc]
        for single_acc in acc:
            in_acc_type = re.sub("\\d+$", "", single_acc).upper()
            if in_acc_type not in self.valid_in_acc_type and not acc_is_searchstr:
                raise ValueError("{} not a valid input type".format(in_acc_type))
            if acc_is_searchstr:
                in_type = "study"
            else:
                in_type = self.valid_in_type[in_acc_type]
        output_columns = out_type[:]
        if detailed:
            output_columns += [
                "experiment_title",
                "experiment_attribute",
                "sample_attribute",
                "run_accession",
                "taxon_id",
                "library_selection",
                "library_layout",
                "library_strategy",
                "library_source",
                "library_name",
                "bases",
                "spots",
                "adapter_spec",
            ]
        if assay:
            if "library_strategy" not in output_columns:
                output_columns += ["library_strategy"]
        if sample_attribute:
            if "sample_attribute" not in output_columns:
                output_columns += ["sample_attribute"]
        output_columns = [x for x in output_columns if x != in_type]
        output_columns = unique(output_columns)
        select_type = [in_type + "_accession"] + output_columns
        select_type_sql = (",").join(select_type)
        sql = (
            "SELECT DISTINCT "
            + select_type_sql
            + " FROM sra_ft WHERE sra_ft MATCH '"
            + " OR ".join(acc)
            + "';"
        )
        df = self.query(sql)
        if not len(df.index):
            sys.stderr.write("Empty results")
            return df
        if "bases" in df.columns:
            if "spots" in df.columns:
                df["avg_read_length"] = df["bases"] / df["spots"]
                df["spots"] = df["spots"].astype(int)
            df["bases"] = df["bases"].astype(int)
        if "taxon_id" in df.columns:
            df["taxon_id"] = df["taxon_id"].fillna(0).astype(int)
            df = df.sort_values(by=["taxon_id"])
            df["organism_name"] = df["taxon_id"].apply(
                lambda taxid: TAXID_TO_NAME[taxid]
            )
            output_columns += ["organism_name"]
        if "experiment_accession" in df.columns and "run_accession" in df.columns:
            df = df.sort_values(by=["experiment_accession", "run_accession"])
        elif "experiment_accession" in df.columns:
            df = df.sort_values(by=["experiment_accession"])
        elif "run_accession" in df.columns:
            df = df.sort_values(by=["run_accession"])
        elif "sample_accession" in df.columns:
            df = df.sort_values(by=["sample_accession"])
        if output_read_lengths and "avg_read_length" in df.columns:
            output_columns = output_columns + ["avg_read_length"]
        metadata_df = df.reset_index(drop=True)
        metadata_df = order_dataframe(metadata_df, output_columns)
        if expand_sample_attributes:
            if "sample_attribute" in metadata_df.columns.tolist():
                metadata_df = expand_sample_attribute_columns(metadata_df)
                metadata_df = metadata_df.drop(columns=["sample_attribute"])
        return metadata_df

    def srp_to_srx(
        self,
        srp,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRP to SRX/SRR.

        Parameters
        ----------
        srp: string
             SRP ID

        Returns
        -------
        srp_to_srx_df: DataFrame
                       DataFrame with two columns for SRX/SRR
        """
        out_type = ["experiment_accession"]
        if detailed:
            out_type += [
                "sample_accession",
                "run_accession",
                "experiment_alias",
                "sample_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        return self.sra_metadata(
            acc=srp,
            out_type=out_type,
            sample_attribute=sample_attribute,
            expand_sample_attributes=expand_sample_attributes,
        )

    def srp_to_srs(
        self,
        srp,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRP to SRS.

        Parameters
        ----------
        srp: string
             SRP ID

        Returns
        -------
        srp_to_srs_df: DataFrame
                       DataFrame with two columns for SRS
        """
        out_type = ["study_accession", "sample_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "run_accession",
                "study_alias",
                "sample_alias",
                "experiment_alias",
                "run_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        df = self.sra_metadata(
            acc=srp,
            out_type=out_type,
            expand_sample_attributes=expand_sample_attributes,
        )
        return df

    def srp_to_srr(
        self,
        srp,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRP to SRR.

        Parameters
        ----------
        srp: string
             SRP ID

        Returns
        -------
        srp_to_srr_df: DataFrame
        """
        out_type = ["study_accession", "run_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "study_alias",
                "experiment_alias",
                "sample_alias",
                "run_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        df = self.sra_metadata(
            acc=srp,
            out_type=out_type,
            expand_sample_attributes=expand_sample_attributes,
        )
        return df

    def srp_to_gse(
        self,
        srp,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRP to GSE

        Parameters
        ----------
        srp: string
             SRP ID

        Returns
        -------
        srp_to_srr_df: DataFrame
        """
        out_type = ["study_accession", "study_alias"]
        if detailed:
            out_type += [
                "experiment_accession",
                "run_accession",
                "sample_accession",
                "experiment_alias",
                "run_alias",
                "sample_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        return self.sra_metadata(
            acc=srp,
            out_type=out_type,
            expand_sample_attributes=expand_sample_attributes,
        )

    def gse_to_srp(
        self,
        gses,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRP to GSE

        Parameters
        ----------
        gses: string or list
              List of GSE ID

        Returns
        -------
        gse_to_srp_df: DataFrame
        """
        gses = _listify(gses)
        out_type = ["study_alias", "study_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "experiment_alias",
                "sample_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gses)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def gsm_to_srp(
        self,
        gsms,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert GSM to SRP.

        Parameters
        ----------
        gsms: string or list
              List of GSM ID

        Returns
        -------
        gsm_to_srp_df: DataFrame
        """
        gsms = _listify(gsms)
        out_type = ["experiment_alias", "study_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "run_accession",
                "experiment_alias",
                "sample_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gsms)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def gsm_to_srr(
        self,
        gsms,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert GSMs to SRR.

        Parameters
        ----------
        gsms: string or list
              List of GSM id
        sample_attribute: bool
                          Include `sample_attribute` column


        Returns
        -------
        gsm_to_srr_df: DataFrame
                       DataFrame with two columns for GSM/SRR
        """
        gsms = _listify(gsms)

        out_type = ["experiment_alias", "run_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "study_accession",
                "run_alias",
                "sample_alias",
                "study_alias",
            ]

        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gsms)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def gsm_to_srs(
        self,
        gsms,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert GSM to SRS.

        Parameters
        ----------
        gsms: list or string
              List of gsms

        Returns
        -------
        gsm_to_srs_df: DataFrame
        """
        gsms = _listify(gsms)
        out_type = ["sample_alias", "sample_accession"]
        if detailed:
            out_type += [
                "sample_accession",
                "experiment_accession",
                "run_accession",
                "study_accession",
                "sample_alias",
                "experiment_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gsms)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def gsm_to_srx(
        self,
        gsms,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert GSM to SRX.

        Parameters
        ----------
        srx: string
             SRX ID

        Returns
        -------
        srs_to_srx_df: DataFrame
        """
        gsms = _listify(gsms)
        out_type = ["experiment_alias", "experiment_accession"]
        if detailed:
            out_type += [
                "sample_accession",
                "run_accession",
                "study_accession",
                "sample_alias",
                "experiment_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gsms)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def gse_to_gsm(
        self,
        gses,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert GSE to GSM

        Parameters
        ----------
        gses: string or list
              List of GSE ID

        Returns
        -------
        gse_to_gsm_df: DataFrame
        """
        gses = _listify(gses)
        out_type = ["study_alias", "experiment_alias"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "run_accession",
                "sample_alias",
                "run_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gses)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def gsm_to_gse(
        self,
        gsms,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert GSM to GSE

        Parameters
        ----------
        gsms: string or list
              List of GSM ID

        Returns
        -------
        gsm_to_gse_df: DataFrame
        """
        gsms = _listify(gsms)
        out_type = ["experiment_alias", "study_alias"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "run_accession",
                "sample_alias",
                "run_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, gsms)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srr_to_srp(
        self,
        srrs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRR to SRP.

        Parameters
        ----------
        srr: list of string
             List of SRR IDs

        Returns
        -------
        srr_to_srp_df: DataFrame
        """
        srrs = _listify(srrs)
        out_type = ["run_accession", "study_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "sample_accession",
                "run_alias",
                "study_alias",
                "experiment_alias",
                "sample_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srrs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srr_to_srs(
        self,
        srrs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRR to SRS.

        Parameters
        ----------
        srr: list of string
             List of SRR IDs

        Returns
        -------
        srp_to_srs_df: DataFrame
        """
        srrs = _listify(srrs)
        out_type = ["run_accession", "sample_accession"]
        if detailed:
            out_type += [
                "experiment_accession",
                "study_accession",
                "run_alias",
                "sample_alias",
                "experiment_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srrs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srx_to_srs(
        self,
        srxs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRX to SRS.

        Parameters
        ----------
        srx: string
             SRX ID

        Returns
        -------
        srp_to_srs_df: DataFrame
        """
        srxs = _listify(srxs)
        out_type = ["experiment_accession", "sample_accession"]
        if detailed:
            out_type += [
                "run_accession",
                "study_accession",
                "experiment_alias",
                "sample_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srxs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srs_to_gsm(
        self,
        srss,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRS to GSM.

        Parameters
        ----------
        srss: list or string
              List of SRS ID

        Returns
        -------
        srs_to_gsm_df: DataFrame
        """
        srss = _listify(srss)
        out_type = ["sample_accession", "sample_alias"]
        if detailed:
            out_type += [
                "experiment_accession",
                "run_accession",
                "study_accession",
                "experiment_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srss)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srs_to_srx(
        self,
        srss,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRS to SRX.

        Parameters
        ----------
        srx: string
             SRX ID

        Returns
        -------
        srs_to_srx_df: DataFrame
        """
        srss = _listify(srss)
        out_type = ["sample_accession", "experiment_accession"]
        if detailed:
            out_type += [
                "run_accession",
                "study_accession",
                "sample_alias",
                "experiment_alias",
                "run_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srss)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srr_to_srx(
        self,
        srrs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRR to SRX.

        Parameters
        ----------
        srrs: string or list
              List of SRR id
        sample_attribute: bool
                          Include `sample_attribute` column


        Returns
        -------
        srr_to_srx_df: DataFrame
                       DataFrame with two columns for SRX/SRR
        """
        srrs = _listify(srrs)

        out_type = ["run_accession", "experiment_accession"]
        if detailed:
            out_type += [
                "sample_accession",
                "study_accession",
                "run_alias",
                "experiment_alias",
                "sample_alias",
                "study_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srrs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srx_to_srp(
        self,
        srxs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRXs to SRP.

        Parameters
        ----------
        srxs: string or list
              List of SRX id
        sample_attribute: bool
                          Include `sample_attribute` column


        Returns
        -------
        srx_to_srp_df: DataFrame
                       DataFrame with two columns for SRX
        """
        srxs = _listify(srxs)
        out_type = ["experiment_accession", "study_accession"]
        if detailed:
            out_type += [
                "run_accession",
                "sample_accession",
                "experiment_alias",
                "run_alias",
                "sample_alias",
                "study_alias",
            ]

        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srxs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srr_to_gsm(
        self,
        srrs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRR to GSM

        Parameters
        ----------
        gses: string or list
              List of SRR

        Returns
        -------
        srr_to_gsm_df: DataFrame
        """
        srrs = _listify(srrs)
        out_type = ["run_alias", "experiment_alias"]
        if detailed:
            out_type += [
                "run_accession",
                "experiment_accession",
                "study_accession",
                "sample_accession",
                "study_alias" "sample_alias",
            ]
        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srrs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def srx_to_srr(
        self,
        srxs,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
    ):
        """Convert SRXs to SRR/SRP.

        Parameters
        ----------
        srxs: string or list
              List of SRX id
        sample_attribute: bool
                          Include `sample_attribute` column


        Returns
        -------
        srx_to_srp_df: DataFrame
                       DataFrame with two columns for SRX/SRR
        """
        srxs = _listify(srxs)
        out_type = ["experiment_accession", "run_accession"]
        if detailed:
            out_type += [
                "sample_accession",
                "study_accession",
                "experiment_alias",
                "run_alias",
                "sample_alias",
                "study_alias",
            ]

        if sample_attribute:
            out_type += ["sample_attribute"]
        select_type_sql = (",").join(out_type)
        sql = _create_query(select_type_sql, srxs)
        df = self.query(sql)
        df = _prettify_df(df, out_type, expand_sample_attributes)
        return df

    def search_sra(
        self,
        search_str,
        out_type=[
            "study_accession",
            "experiment_accession",
            "sample_accession",
            "run_accession",
        ],
        assay=False,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
        output_read_lengths=False,
    ):
        """Search SRA for any search term.

        Parameters
        ----------
        search_str: string
                    SQL like text string to search.
                    SQL like text => For example,
                    terms in quotes "" enforce an exact search.


        Returns
        -------
        query_df: DataFrame
                  Dataframe with relevant query results
        """
        return self.sra_metadata(
            search_str,
            out_type=out_type,
            assay=assay,
            sample_attribute=sample_attribute,
            detailed=detailed,
            expand_sample_attributes=expand_sample_attributes,
            output_read_lengths=output_read_lengths,
            acc_is_searchstr=True,
        )

    def search_by_expt_id(self, srx):
        """Search for a SRX/GSM id in the experiments.

        Parameters
        ----------
        srx: string
             SRX (experiment_accession) ID

        Returns
        -------
        results: dict
                 Dictionary with relevant hits
        """
        if "GSM" in srx:
            results = self.cursor.execute(
                'select * from EXPERIMENT where experiment_alias = "{}"'.format(srx)
            ).fetchall()
        else:
            results = self.cursor.execute(
                'select * from EXPERIMENT where experiment_accession = "{}"'.format(srx)
            ).fetchall()
        assert len(results) == 1, "Got multiple hits"
        results = results[0]
        column_names = list([x[0] for x in self.cursor.description])
        results = dict(list(zip(column_names, results)))
        return pd.DataFrame.from_dict(results, orient="index").T

    @staticmethod
    def _srapath_url(sacc):
        """Get srapath URL for a SRP/SRR.

        Parameters
        ----------
        srp: string


        Returns
        -------
        srr_paths: dict
                   A dict of URLS with keys as SRR
        """
        if PY3_VERSION >= 7:
            proc = subprocess.run(["srapath", sacc], capture_output=True)
        else:
            proc = subprocess.run(["srapath", sacc], stdout=PIPE, stderr=PIPE)
        stdout = str(proc.stdout.strip().decode("utf-8"))

        urls = stdout.split("\n")
        # TODO: Improve this
        if not urls[0]:
            sys.stderr.write("Unable to run srapath.\n")
            return None
        urls = list(map(str, urls))
        srrs = [str(url.strip().split("/")[-1].split(".")[0]) for url in urls]
        return dict(zip(srrs, urls))

    @staticmethod
    def _srapath_url_srr(srr):
        """Get srapath URL for a SRR.

        Parameters
        ----------
        srp: string


        Returns
        -------
        srr_paths: dict
                   A dict of URLS with keys as SRR
        """
        if PY3_VERSION >= 7:
            proc = subprocess.run(["srapath", srr], capture_output=True)
        else:
            proc = subprocess.run(["srapath", srr], stdout=PIPE, stderr=PIPE)
        stdout = str(proc.stdout.strip().decode("utf-8"))
        urls = stdout.split("\n")
        # TODO: Improve this
        if not urls[0]:
            sys.stderr.write("Unable to run srapath.\n")
            return None
        return str(urls[0])

    def download(
        self,
        srp=None,
        df=None,
        url_col="sra_url",
        out_dir=None,
        filter_by_srx=[],
        protocol="ftp",
        ascp_dir=None,
        skip_confirmation=False,
    ):
        """Download SRA files.

        Parameters
        ----------
        srp: string
             SRP ID (optional)
        df: Dataframe
            A dataframe as obtained from `sra_metadata`
        url_col: string
                Column of df to use for downloading
        out_dir: string
                 Directory location for download
        filter_by_srx: list
                       List of SRX ids to filter
        protocol: string
                  ['fasp'/'ftp'] fasp => faster download, ftp => slower
        ascp_dir: string
                  Location of ascp directory
        """
        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads")
        if srp:
            df = self.sra_metadata(srp, detailed=True)
        # if protocol == "ftp":
        #    sys.stderr.write(
        #        dedent("""\
        #    Using `ftp` protocol leads to slower downloads.\n
        #    Consider using `fasp` after installing aspera-client.\n"""))
        if protocol == "fasp":
            if ascp_dir is None:
                ascp_dir = os.path.join(os.path.expanduser("~"), ".aspera")
            if not os.path.exists(ascp_dir):

                sys.stderr.write(
                    "Count not find aspera at: {}\n".format(ascp_dir)
                    + "Install aspera-client following instructions"
                    + "at https://github.com/saketkc/pysradb/README.rst for faster downloads.\n"
                    + "You can supress this message by using `--use-wget` flag\n"
                    + "Continuing with wget ...\n\n"
                )
                protocol = "ftp"
            else:
                ascp_bin = os.path.join(ascp_dir, "connect", "bin", "ascp")
        df = df.copy()
        if filter_by_srx:
            if isinstance(filter_by_srx, str):
                filter_by_srx = [filter_by_srx]
        if filter_by_srx:
            df = df[df.experiment_accession.isin(filter_by_srx)]
        if "sra_url" in df.columns.tolist() or "srapath_url" in df.columns.tolist():
            df["download_url"] = ""
        else:
            df.loc[:, "download_url"] = (
                FTP_PREFIX[protocol]
                + "/sra/sra-instant/reads/ByRun/sra/"
                + df["run_accession"].str[:3]
                + "/"
                + df["run_accession"].str[:6]
                + "/"
                + df["run_accession"]
                + "/"
                + df["run_accession"]
                + ".sra"
            )

        if url_col in df.columns.tolist():
            df = df.rename(columns={url_col: "srapath_url"})
        else:
            df["srapath_url"] = [
                self._srapath_url_srr(srr) for srr in df["run_accession"]
            ]
        download_list = df[
            [
                "study_accession",
                "experiment_accession",
                "run_accession",
                "download_url",
                "srapath_url",
            ]
        ].values
        if not len(df.index):
            print("Could not locate {} in db".format(srp))
            sys.exit(0)
        file_sizes = df.apply(get_file_size, axis=1)
        total_file_size = millify(np.sum(file_sizes))
        print("The following files will be downloaded: \n")
        pd.set_option("display.max_colwidth", -1)
        print(df.to_string(index=False, justify="left", col_space=0))
        print(os.linesep)
        print("Total size: {}".format(total_file_size))
        print(os.linesep)
        if not skip_confirmation:
            if not confirm("Start download? "):
                sys.exit(0)
        with tqdm(total=download_list.shape[0]) as pbar:
            for srp, srx, srr, download_url, srapath_url in download_list:
                pbar.set_description("{}/{}/{}".format(srp, srx, srr))
                srp_dir = os.path.join(out_dir, srp)
                srx_dir = os.path.join(srp_dir, srx)
                download_filename = path_leaf(download_url)
                if ".fastq.gz" not in download_filename:
                    srr_location = os.path.join(srx_dir, srr + ".sra")
                else:
                    srr_location = os.path.join(srx_dir, download_filename)
                mkdir_p(srx_dir)
                if protocol == "fasp":

                    cmd = ASCP_CMD_PREFIX.replace("ascp", ascp_bin)
                    cmd = "{} {} {} {}".format(
                        cmd, _find_aspera_keypath(ascp_dir), download_url, srx_dir
                    )
                    run_command(cmd, verbose=False)
                else:
                    if srapath_url is not None:
                        download_filename = path_leaf(srapath_url)
                        if ".fastq.gz" not in download_filename:
                            srr_location = os.path.join(srx_dir, srr + ".sra")
                        else:
                            srr_location = os.path.join(srx_dir, download_filename)
                        download_file(srapath_url, srr_location)
                    else:
                        download_file(download_url, srr_location)
                pbar.update()
        return df

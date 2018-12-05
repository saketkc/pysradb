"""Methods to interact with SRA"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import gzip
import os
import re
import shutil
import sqlite3
import sys
import warnings

import pandas as pd
from tqdm import tqdm

from .utils import _extract_first_field
from .utils import _find_aspera_keypath
from .utils import _get_url
from .utils import mkdir_p
from .utils import order_dataframe
from .utils import run_command

PY3 = True
if sys.version_info[0] < 3:
    PY3 = False

FTP_PREFIX = {
    'fasp': 'anonftp@ftp-trace.ncbi.nlm.nih.gov:',
    'ftp': 'ftp://ftp-trace.ncbi.nlm.nih.gov'
}
SRADB_URL = [
    'https://s3.amazonaws.com/starbuck1/sradb/SRAmetadb.sqlite.gz',
    'https://gbnci-abcc.ncifcrf.gov/backup/SRAmetadb.sqlite.gz'
]

ASCP_CMD_PREFIX = 'ascp -k 1 -QT -l 2000m -i'


def download_sradb_file(download_dir=os.getcwd(), overwrite=True):
    """Download SRAdb.sqlite file.

    Parameters
    ----------
    download_dir: string
                  Directory to download SRAmetadb.sqlite
    overwrite: bool
               overwrite existing file(s).
               Set to True by default.

    """
    download_location = os.path.join(download_dir, 'SRAmetadb.sqlite.gz')
    download_location_unzip = download_location.rstrip('.gz')

    if os.path.isfile(download_location) and overwrite is False:
        raise RuntimeError(
            '{} already exists! Set `overwrite=True` to redownload.'.forma(
                download_location))
    if os.path.isfile(download_location_unzip) and overwrite is False:
        raise RuntimeError(
            '{} already exists! Set `overwrite=True` to redownload.'.format(
                download_location_unzip))

    try:
        _get_url(SRADB_URL[0], download_location)
    except Exception as e:
        # Try other URL
        warnings.warn(
            'Could not use {}.\nException: {}.\nTrying alternate url ...\n'.
            format(SRADB_URL[0], e), RuntimeWarning)
        _get_url(SRADB_URL[1], download_location)
    print('Extracting {} ...'.format(download_location))
    with gzip.open(download_location, 'rb') as fh_in:
        with open(download_location_unzip, 'wb') as fh_out:
            shutil.copyfileobj(fh_in, fh_out)
    print('Done!')
    db = SRAdb(download_location_unzip)
    metadata = db.query('SELECT * FROM metaInfo')
    db.close()
    print('Metadata associated with {}:'.format(download_location_unzip))
    print(metadata)


class SRAdb(object):
    def __init__(self, sqlite_file):
        """Initialize SRAdb.

        Parameters
        ----------

        sqlite_file: string
                     Path to unzipped SRAmetadb.sqlite file


        """
        self.sqlite_file = sqlite_file
        self.open()
        self.cursor = self.db.cursor()
        self.valid_in_acc_type = [
            'SRA', 'ERA', 'DRA', 'SRP', 'ERP', 'DRP', 'SRS', 'ERS', 'DRS',
            'SRX', 'ERX', 'DRX', 'SRR', 'ERR', 'DRR'
        ]
        self.valid_in_type = {
            'SRA': 'submission',
            'ERA': 'submission',
            'DRA': 'submission',
            'SRP': 'study',
            'ERP': 'study',
            'DRP': 'study',
            'SRS': 'sample',
            'ERS': 'sample',
            'DRS': 'sample',
            'SRX': 'experiment',
            'ERX': 'experiment',
            'DRX': 'experiment',
            'SRR': 'run',
            'ERR': 'run',
            'DRR': 'run'
        }

    def open(self):
        """Open sqlite connection."""
        self.db = sqlite3.connect(self.sqlite_file)
        self.db.text_factory = str

    def close(self):
        """Close sqlite connection."""
        self.db.close()

    def list_tables(self):
        """List all tables in the sqlite file.


        Returns
        -------
        table_list: list
                    List of all table names
        """
        results = self.cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table";').fetchall()
        return _extract_first_field(results)

    def list_fields(self, table):
        """List all fields in a given table.

        Parameters
        ----------
        table: string
               Table name.
               See `list_tables` for getting all table names

        Returns
        -------
        field_list: list
                    A list of field names for the table
        """
        results = self.cursor.execute('SELECT * FROM {}'.format(table))
        return _extract_first_field(results.description)

    def desc_table(self, table):
        """Describe all fields in a table.

        Parameters
        ----------
        table: string
               Table name.
               See `list_tables` for getting all table names

        Returns
        -------
        table_desc: DataFrame
                    A DataFrame with field name and its
                    schema description
        """
        results = self.cursor.execute(
            'PRAGMA table_info("{}")'.format(table)).fetchall()
        columns = ['cid', 'name', 'dtype', 'notnull', 'dflt_value', 'pk']
        data = []
        for result in results:
            data.append(list(map(lambda x: str(x), result)))
        table_desc = pd.DataFrame(data, columns=columns)
        return table_desc

    def query(self, sql_query):
        """Run SQL query.

        Parameters
        ----------
        sql_query: string
                   SQL query string

        Returns
        -------
        results: DataFrame
                 Query results formatted as dataframe

        """
        results = self.cursor.execute(sql_query).fetchall()
        column_names = list(map(lambda x: x[0], self.cursor.description))
        results = [dict(zip(column_names, result)) for result in results]
        return pd.DataFrame(results)

    def get_row_count(self, table):
        """Get row counts for a table.

        Parameters
        ----------
        table: string
               Table name.
               See `list_tables` for getting all table names

        Returns
        -------
        row_count: int
                   Number of rows in table
        """
        return self.cursor.execute(
            'SELECT max(rowid) FROM {}'.format(table)).fetchone()[0]

    def all_row_counts(self):
        """Get row counts of all tables in the db file.

        Returns
        -------
        row_counts: DataFrame
                    A dataframe with table names and corresponding
                    row count.

        """
        tables = self.list_tables()
        results = dict(
            [(table, self.get_row_count(table)) for table in tables])
        return pd.DataFrame.from_dict(
            results, orient='index', columns=['count'])

    def sra_metadata(self,
                     acc,
                     out_type=[
                         'study_accession',
                         'experiment_accession',
                         'experiment_title',
                         'experiment_attribute',
                         'sample_attribute',
                         'run_accession',
                         'taxon_id',
                         'library_selection',
                         'library_layout',
                         'library_strategy',
                         'library_source',
                         'library_name',
                         'bases',
                         'spots',
                         'adapter_spec',
                     ],
                     expand_sample_attributes=False):
        """Get metadata for the provided SRA accession.

        Parameters
        ----------
        acc: string
             SRA accession ID
        out_type: list
                  List of columns to output

        Returns
        -------
        metadata_df: DataFrame
                     A dataframe with all relevant columns
        """
        in_acc_type = re.sub('\\d+$', '', acc).upper()
        if in_acc_type not in self.valid_in_acc_type:
            raise ValueError('{} not a valid input type'.format(in_acc_type))

        in_type = self.valid_in_type[in_acc_type]
        out_type = [x for x in out_type if x != in_type]

        select_type = [in_type + '_accession'] + out_type
        select_type_sql = (',').join(select_type)
        sql = "SELECT DISTINCT " + select_type_sql + " FROM sra_ft WHERE sra_ft MATCH '" + acc + "';"
        df = self.query(sql)
        df['avg_read_length'] = df['bases'] / df['spots']
        df['spots'] = df['spots'].astype(int)
        df['bases'] = df['bases'].astype(int)
        df['taxon_id'] = df['taxon_id'].fillna(0).astype(int)
        df = df.sort_values(by=[
            'taxon_id', 'avg_read_length', 'run_accession',
            'experiment_accession', 'library_selection'
        ])
        metadata_df = df[out_type + ['avg_read_length']].reset_index(drop=True)
        if expand_sample_attributes:
            pass
        return metadata_df

    def search_sra(
            self,
            search_str,
            out_type=[
                'study_accession', 'experiment_accession', 'experiment_title',
                'experiment_attribute', 'sample_attribute', 'run_accession',
                'taxon_id', 'library_selection', 'library_layout',
                'library_strategy', 'library_source', 'library_name', 'bases',
                'spots'
            ]):
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

        select_type = out_type
        select_type_sql = (',').join(select_type)
        sql = "SELECT DISTINCT " + select_type_sql + " FROM sra_ft WHERE sra_ft MATCH '" + search_str + "';"
        df = self.query(sql)
        return order_dataframe(df, out_type)

    def search_experiment(self, srx):
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
        if 'GSM' in srx:
            results = self.cursor.execute(
                'select * from EXPERIMENT where experiment_alias = "{}"'.
                format(srx)).fetchall()
        else:
            results = self.cursor.execute(
                'select * from EXPERIMENT where experiment_accession = "{}"'.
                format(srx)).fetchall()
        assert len(results) == 1, 'Got multiple hits'
        results = results[0]
        column_names = list(map(lambda x: x[0], self.cursor.description))
        results = dict(zip(column_names, results))
        return results

    def convert_gse_to_srp(self, gse):
        """Convert GSE to SRP id.

        Requires input db to be GEOmetadb.sqlite.

        Parameters
        ----------
        gse: string
             GSE ID

        Returns
        -------
        srp: string
             SRP ID
        """
        results = self.query('SELECT * from gse WHERE gse = "' + gse + '"')
        if results.shape[0] == 1:
            splitted = results['supplementary_file'][0].split(';')
            if len(splitted):
                match = re.findall('SRP.*', splitted[-1])
                if len(match):
                    srp = match[0].split('/')[-1]
                    return srp

    def download(self,
                 srp=None,
                 df=None,
                 out_dir=None,
                 protocol='fasp',
                 ascp_dir=None):
        """Download SRA files.

        Parameters
        ----------
        srp: string
             SRP ID (optional)
        df: Dataframe
            A dataframe as obtained from `sra_metadata`
        out_dir: string
                 Directory location for download
        protocol: string
                  ['fasp'/'ftp'] fasp => faster download, ftp => slower
        ascp_dir: string
                  Location of ascp directory
        """
        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), 'pysradb_downloads')
        if srp:
            df = self.sra_metadata(srp)
        if protocol == 'ftp':
            warnings.warn(
                'Using `ftp` protocol leads to slower downloads.\n Consider using `fastp` after installing aspera-client.',
                UserWarning)
        if protocol == 'fasp':
            if ascp_dir is None:
                ascp_dir = os.path.join(os.path.expanduser('~'), '.aspera')
            if not os.path.exists(ascp_dir):
                raise RuntimeError(
                    'Count not find aspera at: {}\n Install aspera-client following instructions in the README.rst OR set `protocol`=ftp.\n'
                    .format(ascp_dir))
            ascp_bin = os.path.join(ascp_dir, 'connect', 'bin', 'ascp')
        df = df.copy()
        df.loc[:, 'download_url'] = FTP_PREFIX[
            protocol] + '/sra/sra-instant/reads/ByRun/sra/' + df[
                'run_accession'].str[:3] + '/' + df[
                    'run_accession'].str[:6] + '/' + df[
                        'run_accession'] + '/' + df['run_accession'] + '.sra'
        download_list = df[[
            'study_accession', 'experiment_accession', 'run_accession',
            'download_url'
        ]].values
        with tqdm(total=download_list.shape[0]) as pbar:
            for srp, srx, srr, url in download_list:
                pbar.set_description('{}/{}/{}'.format(srp, srx, srr))
                srp_dir = os.path.join(out_dir, srp)
                srx_dir = os.path.join(srp_dir, srx)
                srr_location = os.path.join(srx_dir, srr + '.sra')
                mkdir_p(srx_dir)
                if protocol == 'fasp':
                    cmd = ASCP_CMD_PREFIX.replace('ascp', ascp_bin)
                    cmd = '{} {} {} {}'.format(cmd,
                                               _find_aspera_keypath(ascp_dir),
                                               url, srx_dir)
                    run_command(cmd, verbose=False)
                else:
                    _get_url(url, srr_location, show_progress=False)
                pbar.update()
        return df

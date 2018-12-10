"""Methods to interact with SRA"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import gzip
import os
import re
import sys
import warnings

import pandas as pd
from tqdm import tqdm

from .basedb import BASEdb

from .filter_attrs import expand_sample_attribute_columns

from .utils import _find_aspera_keypath
from .utils import _get_url
from .utils import get_gzip_uncompressed_size
from .utils import copyfileobj
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
    if os.path.isfile(download_location_unzip):
        os.remove(download_location_unzip)
    if os.path.isfile(download_location):
        os.remove(download_location)
    try:
        _get_url(SRADB_URL[0], download_location)
    except Exception as e:
        # Try other URL
        warnings.warn(
            'Could not use {}.\nException: {}.\nTrying alternate url ...\n'.
            format(SRADB_URL[0], e), RuntimeWarning)
        _get_url(SRADB_URL[1], download_location)
    print('Extracting {} ...'.format(download_location))
    filesize = get_gzip_uncompressed_size(download_location)
    with gzip.open(download_location, 'rb') as fh_in:
        with open(download_location_unzip, 'wb') as fh_out:
            copyfileobj(
                fh_in,
                fh_out,
                filesize=filesize,
                desc='Extracting {}'.format('SRAmetadb.sqlite.gz'))
    print('Done!')
    db = SRAdb(download_location_unzip)
    metadata = db.query('SELECT * FROM metaInfo')
    db.close()
    print('Metadata associated with {}:'.format(download_location_unzip))
    print(metadata)


class SRAdb(BASEdb):
    def __init__(self, sqlite_file):
        """Initialize SRAdb.

        Parameters
        ----------

        sqlite_file: string
                     Path to unzipped SRAmetadb.sqlite file


        """
        super(SRAdb, self).__init__(sqlite_file)
        self._db_type = 'SRA'
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
        expand_sample_attributes: bool
                                  Should sample_attribute column be expanded?

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
        sql = "SELECT DISTINCT " + select_type_sql + \
              " FROM sra_ft WHERE sra_ft MATCH '" + acc + "';"
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
            if 'sample_attribute' in metadata_df.columns:
                metadata_df = expand_sample_attribute_columns(metadata_df)
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
        sql = "SELECT DISTINCT " + select_type_sql +\
              " FROM sra_ft WHERE sra_ft MATCH '" + search_str + "';"
        df = self.query(sql)
        if len(df.index) > 0:
            return order_dataframe(df, out_type)
        return None

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
        return pd.DataFrame.from_dict(results, orient='index').T

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
                '''Using `ftp` protocol leads to slower downloads.\n
                Consider using `fasp` after installing aspera-client.''',
                UserWarning)
        if protocol == 'fasp':
            if ascp_dir is None:
                ascp_dir = os.path.join(os.path.expanduser('~'), '.aspera')
            if not os.path.exists(ascp_dir):
                raise RuntimeError('''Count not find aspera at: {}\n
                    Install aspera-client following instructions
                    in the README.rst OR set `protocol`=ftp.\n'''.format(
                    ascp_dir))
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

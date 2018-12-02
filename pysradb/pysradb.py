"""Methods to interact with SRA"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import errno
import os
import re
import shlex
import sqlite3
import subprocess

import pandas as pd
from tqdm import tqdm

FTP_PREFIX = {
    'fasp': 'anonftp@ftp-trace.ncbi.nlm.nih.gov:',
    'ftp': 'ftp://ftp-trace.ncbi.nlm.nih.gov'
}
ASCP_CMD_PREFIX = 'ascp -k 1 -QT -l 2000m -i'


def _find_aspera_keypath(aspera_dir=None):
    """Locate aspera key.

    Parameters
    ----------
    aspera_dir: string
                Location to aspera directory (optional)

    Returns
    -------
    aspera_keypath: string
                    Location to aspera key
    """
    if aspera_dir is None:
        aspera_dir = os.path.join(os.path.expanduser('~'), '.aspera')
    aspera_keypath = os.path.join(aspera_dir, 'connect', 'etc',
                                  'asperaweb_id_dsa.openssh')
    if os.path.isfile(aspera_keypath):
        return aspera_keypath


def _extract_first_field(data):
    """Extract first field from a list of fields"""
    return list(next(zip(*data)))


def mkdir_p(path):
    """Python version mkdir -p

    Parameters
    ----------
    path : string
           Path to directory to create
    """
    if path:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def run_command(command, verbose=False):
    """Run a shell command"""
    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf8')
    while True:
        output = str(process.stdout.readline().strip())
        if output == '' and process.poll() is not None:
            break
        if output:
            if verbose:
                print(str(output.strip()))
    rc = process.poll()
    return rc


class SRAdb(object):
    def __init__(self, sqlite_file):
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
        self.db = sqlite3.connect(self.sqlite_file)
        self.db.text_factory = str

    def close(self):
        self.db.close()

    def list_tables(self):
        """List all tables in the sqlite"""
        results = self.cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table";').fetchall()
        return _extract_first_field(results)

    def list_fields(self, table):
        "List all fields in a given table"
        results = self.cursor.execute('SELECT * FROM {}'.format(table))
        return _extract_first_field(results.description)

    def desc_table(self, table):
        results = self.cursor.execute(
            'PRAGMA table_info("{}")'.format(table)).fetchall()
        columns = ['cid', 'name', 'dtype', 'notnull', 'dflt_value', 'pk']
        data = []
        for result in results:
            data.append(list(map(lambda x: str(x), result)))
        df = pd.DataFrame(data, columns=columns)
        return df

    def get_query(self, query):
        results = self.cursor.execute(query).fetchall()
        column_names = list(map(lambda x: x[0], self.cursor.description))
        results = [dict(zip(column_names, result)) for result in results]
        return pd.DataFrame(results)

    def get_row_count(self, table):
        """Get row counts for a table"""
        return self.cursor.execute(
            'SELECT max(rowid) FROM {}'.format(table)).fetchone()[0]

    def get_table_counts(self):
        tables = self.list_tables()
        results = dict(
            [(table, self.get_row_count(table)) for table in tables])
        return pd.DataFrame.from_dict(
            results, orient='index', columns=['count'])

    def sra_convert(self,
                    acc,
                    out_type=[
                        'study_accession',
                        'experiment_accession',
                        'experiment_title',
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
                    ]):
        in_acc_type = re.sub('\\d+$', '', acc).upper()
        if in_acc_type not in self.valid_in_acc_type:
            raise ValueError('{} not a valid input type'.format(in_acc_type))

        in_type = self.valid_in_type[in_acc_type]
        out_type = [x for x in out_type if x != in_type]

        select_type = [in_type + '_accession'] + out_type
        select_type_sql = (',').join(select_type)
        sql = "SELECT DISTINCT " + select_type_sql + " FROM sra_ft WHERE sra_ft MATCH '" + acc + "';"
        df = self.get_query(sql)
        df['avg_read_length'] = df['bases'] / df['spots']
        df['spots'] = df['spots'].astype(int)
        df['bases'] = df['bases'].astype(int)
        df['taxon_id'] = df['taxon_id'].fillna(0).astype(int)
        df = df.sort_values(by=[
            'taxon_id', 'avg_read_length', 'run_accession',
            'experiment_accession', 'library_selection'
        ])
        df = df[out_type + ['avg_read_length']].reset_index(drop=True)
        return df

    def search_experiment(self, srx):
        """Search for a SRX/GSM id in the experiments"""
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
        results = self.get_query('SELECT * from gse WHERE gse = "' + gse + '"')
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
                 ascp_dir=None,
                 verbose=False):
        """Download SRA files

        Parameters
        ----------
        srp: string
             SRP ID (optional)
        df: Dataframe
            A dataframe as obtained from `sra_convert`
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
            df = self.sra_convert(srp)
        df.loc[:, 'download_url'] = FTP_PREFIX[
            protocol] + '/sra/sra-instant/reads/ByRun/sra/' + df[
                'run_accession'].str[:3] + '/' + df[
                    'run_accession'].str[:6] + '/' + df[
                        'run_accession'] + '/' + df['run_accession'] + '.sra'
        download_list = df[[
            'study_accession', 'experiment_accession', 'download_url'
        ]].values
        with tqdm(total=download_list.shape[0]) as pbar:
            for srp, srx, url in download_list:
                srp_dir = os.path.join(out_dir, srp)
                srx_dir = os.path.join(srp_dir, srx)
                mkdir_p(srx_dir)
                if verbose:
                    print('Downloading {}....'.format(url))
                if ascp_dir is None:
                    ascp_dir = os.path.join(os.path.expanduser('~'), '.aspera')
                ascp_bin = os.path.join(ascp_dir, 'connect', 'bin', 'ascp')
                cmd = ASCP_CMD_PREFIX.replace('ascp', ascp_bin)
                cmd = '{} {} {} {}'.format(cmd, _find_aspera_keypath(ascp_dir),
                                           url, srx_dir)
                run_command(cmd, verbose)
                if verbose:
                    print('Finished {}....'.format(url))
                pbar.update()
        return df

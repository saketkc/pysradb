"""Command line interface for pysradb
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
import sys

from . import __version__
from .sradb import download_sradb_file
from .sradb import SRAdb
from .geodb import download_geodb_file
from .geodb import GEOdb

import click
import pandas as pd

click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

PY3 = True
if sys.version_info[0] < 3:
    PY3 = False

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO

def _check_sradb_file(db):
    if db is None:
        db = os.path.join(os.getcwd(), 'SRAmetadb.sqlite')
        download_sradb_file()
    if not os.path.isfile(db):
        raise RuntimeError('{} does not exist'.format(db))
    return db


def _check_geodb_file(db):
    if db is None:
        db = os.path.join(os.getcwd(), 'GEOmetadb.sqlite')
        download_geodb_file()
    if not os.path.isfile(db):
        raise RuntimeError('{} does not exist'.format(db))
    return db


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.

    Citation: Pending.
    """
    pass


@cli.command(
    'srametadb',
    context_settings=CONTEXT_SETTINGS,
    help='Download SRAmetadb.sqlite')
@click.option('--out_dir', type=str, help='Output directory location')
@click.option('--overwrite', type=bool, help='Overwrite existing file')
def cmd_download_sra(out_dir, overwrite):
    if out_dir is None:
        out_dir = os.getcwd()
    download_sradb_file(out_dir, overwrite)


@cli.command(
    'geometadb',
    context_settings=CONTEXT_SETTINGS,
    help='Download GEOmetadb.sqlite')
@click.option('--out_dir', type=str, help='Output directory location')
@click.option('--overwrite', type=bool, help='Overwrite existing file')
def cmd_download_geo(out_dir, overwrite):
    if out_dir is None:
        out_dir = os.getcwd()
    download_geodb_file(out_dir, overwrite)


@cli.command(
    'download',
    context_settings=CONTEXT_SETTINGS,
    help='Download SRA project (SRPnnnn)')
@click.option('--out_dir', help='Output directory root')
@click.option(
    '--db',
    help='Path to SRAmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.option('--srx', '-x', help='Download only these SRX(s)', multiple=True)
@click.option('--srp', '-p', help='SRP ID', multiple=True)
def cmd_download_sra(out_dir, db, srx, srp):
    db = _check_sradb_file(db)
    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), 'pysradb_downloads')
    sradb = SRAdb(db)
    if not srp:
        stdin_text = click.get_text_stream('stdin').read()#.replace('\t', '  ')#.strip()
        text = ''
        for line in stdin_text.split('\n'):
            line = line.strip()
            line = line.lstrip(' ')
            line = re.sub( '\s+', ' ', line).strip()
            text += '{}\n'.format(line)
        print(text)
        df = pd.read_csv(StringIO(text), sep=' ')
        print(df)
        sradb.download(df=df, out_dir=out_dir, filter_by_srx=srx)
    else:
        for srp_x in sorted(unique(srp)):
            sradb.download(srp=srp_x, out_dir=out_dir, filter_by_srx=srx)
    sradb.close()


@cli.command(
    'sra-metadata',
    context_settings=CONTEXT_SETTINGS,
    help='Fetch metadata for SRA project (SRPnnnn)')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option(
    '--db',
    help='Path to SRAmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--assay',
    is_flag=True,
    help='Include assay type in output',
    default=False)
@click.option(
    '--desc',
    is_flag=True,
    help='Should sample_attribute be included',
    default=False)
@click.option(
    '--detailed',
    is_flag=True,
    help='Display detailed metadata table',
    default=False)
@click.option(
    '--expand',
    is_flag=True,
    help='Should sample_attribute be expanded',
    default=False)
@click.argument('srp_id', required=True)
def cmd_sra_metadata(srp_id, db, assay, desc, detailed, expand, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.sra_metadata(
        acc=srp_id,
        assay=assay,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))

    sradb.close()


@cli.command(
    'srp-to-srx',
    context_settings=CONTEXT_SETTINGS,
    help='Get SRX/SRR for a SRP')
@click.option(
    '--db',
    help='Path to SRAmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.option('--saveto', help='Save output to file')
@click.argument('srp_id', required=True)
def cmd_srp_to_srx(srp_id, db, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srp_to_srx(srp=srp_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))
    sradb.close()


@cli.command(
    'srr-to-srx',
    context_settings=CONTEXT_SETTINGS,
    help='Get SRP/SRX for a SRR')
@click.option(
    '--db',
    help='Path to SRAmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--desc',
    is_flag=True,
    help='Should sample_attribute be included',
    default=False)
@click.option('--saveto', help='Save output to file')
@click.argument('srr_ids', nargs=-1, required=True)
def cmd_srp_to_srx(srr_ids, desc, db, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srr_to_srx(srrs=srr_ids, sample_attribute=desc)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))
    sradb.close()


@cli.command(
    'srx-to-srr',
    context_settings=CONTEXT_SETTINGS,
    help='Get SRR/SRP for a SRX')
@click.option(
    '--db',
    help='Path to SRAmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--desc',
    is_flag=True,
    help='Should sample_attribute be included',
    default=False)
@click.option('--saveto', help='Save output to file')
@click.argument('srx_ids', nargs=-1, required=True)
def cmd_srp_to_srx(srx_ids, desc, db, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srx_to_srr(srxs=srx_ids, sample_attribute=desc)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))
    sradb.close()


@cli.command(
    'gse-metadata',
    context_settings=CONTEXT_SETTINGS,
    help='Fetch metadata for GEO ID (GSEnnnn)')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option(
    '--db',
    help='Path to GEOmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.argument('gse_id', required=True)
def cmd_gse_metadata(gse_id, db, saveto):
    db = _check_geodb_file(db)
    geodb = GEOdb(db)
    df = geodb.gse_metadata(gse=gse_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))
    geodb.close()


@cli.command(
    'gsm-metadata',
    context_settings=CONTEXT_SETTINGS,
    help='Fetch metadata for GSM ID (GSMnnnn)')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option(
    '--db',
    help='Path to GEOmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.argument('gsm_id', required=True)
def cmd_gsm_metadata(gsm_id, db, saveto):
    db = _check_geodb_file(db)
    geodb = GEOdb(db)
    df = geodb.gsm_metadata(gsm=gsm_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))
    geodb.close()


@cli.command(
    'gse-to-gsm', context_settings=CONTEXT_SETTINGS, help='Get GSM(s) for GSE')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option(
    '--db',
    help='Path to GEOmetadb.sqlite file',
    type=click.Path(exists=True, dir_okay=False))
@click.argument('gse_id', required=True)
def cmd_gse_to_gsm(gse_id, db, saveto):
    db = _check_geodb_file(db)
    geodb = GEOdb(db)
    df = geodb.gse_to_gsm(gse=gse_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        if len(df.index):
            if PY3:
                pd.set_option('display.max_colwidth', -1)
                print(df.to_string(index=False, justify='left', col_space=0))
            else:
                print(
                    df.to_string(index=False, justify='left',
                                 col_space=0).encode('utf-8'))
    geodb.close()

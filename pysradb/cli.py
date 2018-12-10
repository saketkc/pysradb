"""Command line interface for pysradb
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from . import __version__
from .sradb import download_sradb_file
from .sradb import SRAdb
from .geodb import download_geodb_file
from .geodb import GEOdb

import click
import pandas as pd

click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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


@click.group()
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
@click.option('--db', help='Path to SRAmetadb.sqlite file')
@click.argument('srp_ids', nargs=-1, required=True)
def cmd_download_sra(out_dir, db, srp_ids):
    db = _check_sradb_file(db)
    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), 'pysradb_downloads')
    sradb = SRAdb(db)
    for srp in srp_ids:
        sradb.download(srp=srp, out_dir=out_dir)
    sradb.close()


@cli.command(
    'sra-metadata',
    context_settings=CONTEXT_SETTINGS,
    help='Fetch metadata for SRA project (SRPnnnn)')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option('--db', help='Path to SRAmetadb.sqlite file')
@click.option(
    '--expand',
    is_flag=True,
    help='Should sample_attribute be expanded',
    default=False)
@click.argument('srp_id', required=True)
def cmd_sra_metadata(srp_id, db, expand, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.sra_metadata(acc=srp_id, expand_sample_attributes=expand)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):
            if len(df.index):
                print(df)
    sradb.close()


@cli.command(
    'gse-metadata',
    context_settings=CONTEXT_SETTINGS,
    help='Fetch metadata for GEO ID (GSEnnnn)')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option('--db', help='Path to GEOmetadb.sqlite file')
@click.argument('gse_id', required=True)
def cmd_gse_metadata(gse_id, db, saveto):
    db = _check_geodb_file(db)
    geodb = GEOdb(db)
    df = geodb.gse_metadata(gse=gse_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):
            if len(df.index):
                print(df)
    geodb.close()


@cli.command(
    'gsm-metadata',
    context_settings=CONTEXT_SETTINGS,
    help='Fetch metadata for GSM ID (GSMnnnn)')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option('--db', help='Path to GEOmetadb.sqlite file')
@click.argument('gsm_id', required=True)
def cmd_gsm_metadata(gsm_id, db, saveto):
    db = _check_geodb_file(db)
    geodb = GEOdb(db)
    df = geodb.gsm_metadata(gsm=gsm_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):
            if len(df.index):
                print(df)
    geodb.close()


@cli.command(
    'gse-to-gsm', context_settings=CONTEXT_SETTINGS, help='Get GSM(s) for GSE')
@click.option('--saveto', help='Save metadata dataframe to file')
@click.option('--db', help='Path to GEOmetadb.sqlite file')
@click.argument('gse_id', required=True)
def cmd_gse_to_gsm(gse_id, db, saveto):
    db = _check_geodb_file(db)
    geodb = GEOdb(db)
    df = geodb.gse_to_gsm(gse=gse_id)
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep='\t')
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):
            if len(df.index):
                print(df)
    geodb.close()

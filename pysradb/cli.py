"""Command line interface for pysradb
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re
import sys
from textwrap import dedent

from . import __version__
from .sradb import download_sradb_file
from .sradb import SRAdb
from .geodb import download_geodb_file
from .geodb import GEOdb

import click
import pandas as pd

click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

from io import StringIO


def _print_save_df(df, saveto=None):
    if saveto:
        df.to_csv(saveto, index=False, header=True, sep="\t")
    else:
        if len(df.index):
            pd.set_option("display.max_colwidth", -1)
            print(df.to_string(index=False, justify="left", col_space=0))


def _check_sradb_file(db):
    if db is None:
        db = os.path.join(os.getcwd(), "SRAmetadb.sqlite")
        if os.path.isfile(db):
            return db
        if click.confirm(
            "SRAmetadb.sqlite file was not found in the current directory. Please quit and specify the path using `--db <DB_PATH>`"
            + os.linesep
            + "Otherwise, should I download SRAmetadb.sqlite in the current directory?"
        ):
            download_sradb_file()
        else:
            sys.exit(1)

    if not os.path.isfile(db):
        raise RuntimeError("{} does not exist".format(db))
    return db


def _check_geodb_file(db):
    if db is None:
        db = os.path.join(os.getcwd(), "GEOmetadb.sqlite")
        download_geodb_file()
    if not os.path.isfile(db):
        raise RuntimeError("{} does not exist".format(db))
    return db


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.

    Citation: Pending.
    """
    pass


@cli.command(
    "metadb", context_settings=CONTEXT_SETTINGS, help="Download SRAmetadb.sqlite"
)
@click.option("--out-dir", type=str, help="Output directory location")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@click.option("--keep-gz", is_flag=True, help="Overwrite existing file")
def cmd_download_sradb(out_dir, overwrite, keep_gz):
    if out_dir is None:
        out_dir = os.getcwd()
    download_sradb_file(out_dir, overwrite, keep_gz)


@cli.command(
    "download", context_settings=CONTEXT_SETTINGS, help="Download SRA project (SRPnnnn)"
)
@click.option("--out-dir", help="Output directory root")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--srx", "-x", help="Download only these SRX(s)", multiple=True)
@click.option("--srp", "-p", help="SRP ID", multiple=True)
@click.option("--skip-confirmation", "-y", is_flag=True, help="Skip confirmation")
@click.option("--use-wget", "-w", is_flag=True, help="Use wget instead of aspera")
def cmd_download_sra(out_dir, db, srx, srp, skip_confirmation, use_wget):
    if use_wget:
        protocol = "ftp"
    else:
        protocol = "fasp"
    db = _check_sradb_file(db)
    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), "pysradb_downloads")
    sradb = SRAdb(db)
    if not srp:
        stdin_text = click.get_text_stream(
            "stdin"
        ).read()  # .replace('\t', '  ')#.strip()
        text = ""
        for index, line in enumerate(stdin_text.split("\n")):
            line = line.strip()
            line = line.lstrip(" ")
            # pandas has different paddings to indent,
            # we cannot replace all sapces at once since the description column
            # can have text with space
            line = re.sub("\s\s\s", "\t", line)
            line = re.sub("\s\s", "\t", line)
            line = re.sub("\t+", "\t", line)
            line = re.sub("\s\t", "\t", line)
            line = re.sub("\t\s", "\t", line)

            if index == 0:
                # For first line which is the header, allow substituting spaces with tab at once
                line = re.sub("\s+", "\t", line)

            text += "{}\n".format(line)
        df = pd.read_csv(StringIO(text), sep="\t")
        sradb.download(
            df=df,
            out_dir=out_dir,
            filter_by_srx=srx,
            skip_confirmation=skip_confirmation,
            protocol=protocol,
        )
    else:
        for srp_x in sorted(set(srp)):
            sradb.download(
                srp=srp_x,
                out_dir=out_dir,
                filter_by_srx=srx,
                skip_confirmation=skip_confirmation,
            )
    sradb.close()


@cli.command(
    "metadata",
    context_settings=CONTEXT_SETTINGS,
    help="Fetch metadata for SRA project (SRPnnnn)",
)
@click.option("--saveto", help="Save metadata dataframe to file")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--assay", is_flag=True, help="Include assay type in output", default=False
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed", is_flag=True, help="Display detailed metadata table", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srp_id", required=True)
def cmd_sra_metadata(srp_id, db, assay, desc, detailed, expand, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.sra_metadata(
        acc=srp_id,
        assay=assay,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command(
    "search", context_settings=CONTEXT_SETTINGS, help="Search SRA for matching text"
)
@click.option("--saveto", help="Save metadata dataframe to file")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--assay", is_flag=True, help="Include assay type in output", default=False
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed", is_flag=True, help="Display detailed metadata table", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("search_text", required=True)
def cmd_sra_search(search_text, db, assay, desc, detailed, expand, saveto):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.search_sra(
        search_text,
        assay=assay,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srp-to-srx", context_settings=CONTEXT_SETTINGS, help="Get SRX for a SRP")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [sample_accession (SRS),
                                        run_accession (SRR),
                                        experiment_alias (GSM),
                                        sample_alias (GSM_),
                                        run_alias (GSM_r)',
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srp_id", required=True)
def cmd_srp_to_srx(srp_id, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srp_to_srx(
        srp=srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srp-to-srs", context_settings=CONTEXT_SETTINGS, help="Get SRS for a SRP")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [run_accession (SRR),
                                        study_accession (SRP),
                                        experiment_alias (GSM),
                                        sample_alias (GSM_),
                                        run_alias (GSM_r),
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srp_id", required=True)
def cmd_srp_to_srs(srp_id, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srp_to_srs(
        srp=srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srp-to-srr", context_settings=CONTEXT_SETTINGS, help="Get SRR for a SRP")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [experiment_accession (SRX),
                                        sample_accession (SRS),
                                        study_alias (GSE),
                                        experiment_alias (GSM),
                                        sample_alias (GSM_),
                                        run_alias (GSM_r)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srp_id", required=True)
def cmd_srp_to_srr(srp_id, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srp_to_srr(
        srp=srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srp-to-gse", context_settings=CONTEXT_SETTINGS, help="Get GSE for a SRP")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="Output additional columns: [sample_accession, run_accession]",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srp_id", required=True)
def cmd_srp_to_gse(srp_id, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srp_to_gse(
        srp=srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("gse-to-srp", context_settings=CONTEXT_SETTINGS, help="Get SRP for a GSE")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [experiment_accession (SRX),
                                       run_accession (SRR),
                                       sample_accession (SRS),
                                       experiment_alias (GSM_),
                                       run_alias (GSM_r),
                                       sample_alias (GSM)]
                                       """,
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("gse_ids", nargs=-1, required=True)
def cmd_srp_to_gse(gse_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.gse_to_srp(
        gses=gse_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("gse-to-gsm", context_settings=CONTEXT_SETTINGS, help="Get GSM for a GSE")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [sample_accession (SRS),
                                     run_accession (SRR),
                                     sample_alias (GSM),
                                     run_alias (GSM_r)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("gse_ids", nargs=-1, required=True)
def cmd_gse_to_gsm(gse_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.gse_to_gsm(
        gses=gse_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("gsm-to-gse", context_settings=CONTEXT_SETTINGS, help="Get GSE for a GSM")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [sample_accession (SRS),
                                        run_accession (SRR),
                                        sample_alias (GSM),
                                        run_alias (GSM_r)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("gsm_ids", nargs=-1, required=True)
def cmd_gsm_to_gse(gsm_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.gsm_to_gse(
        gsms=gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("gsm-to-srp", context_settings=CONTEXT_SETTINGS, help="Get SRP for a GSM")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [experiment_accession (SRX),
                                        sample_accession (SRS),
                                        run_accession (SRR),
                                        experiment_alias (GSM),
                                        sample_alias (GSM),
                                        run_alias (GSM_r),
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("gsm_ids", nargs=-1, required=True)
def cmd_gsm_to_srp(gsm_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.gsm_to_srp(
        gsms=gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("gsm-to-srr", context_settings=CONTEXT_SETTINGS, help="Get SRR for a GSM")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [experiment_accession (SRX),
                                        sample_accession (SRS),
                                        study_accession (SRS),
                                        run_alias (GSM_r),
                                        sample_alias (GSM),
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("gsm_ids", nargs=-1, required=True)
def cmd_gsm_to_srr(gsm_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.gsm_to_srr(
        gsms=gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("gsm-to-srx", context_settings=CONTEXT_SETTINGS, help="Get SRX for a GSM")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [experiment_accession (SRX),
                                        sample_accession (SRS),
                                        run_accession (SRR),
                                        experiment_alias (GSM),
                                        sample_alias (GSM),
                                        run_alias (GSM_r),
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("gsm_ids", nargs=-1, required=True)
def cmd_gsm_to_srx(gsm_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.gsm_to_srx(
        gsms=gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srx-to-srs", context_settings=CONTEXT_SETTINGS, help="Get SRS for a SRX")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="Output additional columns: [run_accession, study_accession]",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srx_ids", nargs=-1, required=True)
def cmd_srx_to_srs(srx_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srx_to_srs(
        srxs=srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srs-to-srx", context_settings=CONTEXT_SETTINGS, help="Get SRX for a SRS")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--saveto", help="Save output to file")
@click.option(
    "--detailed",
    is_flag=True,
    help="Output additional columns: [run_accession, study_accession]",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.argument("srs_ids", nargs=-1, required=True)
def cmd_srs_to_srx(srs_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srs_to_srx(
        srss=srs_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srr-to-srp", context_settings=CONTEXT_SETTINGS, help="Get SRP for a SRR")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""'Output additional columns: [experiment_accession (SRX),
                                         sample_accession (SRS),
                                         run_alias (GSM_r),
                                         experiment_alias (GSM),
                                         sample_alias (GSM_),
                                         study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("srr_ids", nargs=-1, required=True)
def cmd_srr_to_srp(srr_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srr_to_srp(
        srrs=srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srr-to-gsm", context_settings=CONTEXT_SETTINGS, help="Get GSM for a SRR")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""'Output additional columns: [experiment_accession (SRX),
                                         study_accession (SRP),
                                         run_alias (GSM_r),
                                         sample_alias (GSM_),
                                         experiment_alias (GSM),
                                         study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("srr_ids", nargs=-1, required=True)
def cmd_srr_to_gsm(srr_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srr_to_gsm(
        srrs=srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srr-to-srs", context_settings=CONTEXT_SETTINGS, help="Get SRS for a SRR")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""'Output additional columns: [experiment_accession (SRX),
                                         study_accession (SRP),
                                         run_alias (GSM_r),
                                         sample_alias (GSM_),
                                         experiment_alias (GSM),
                                         study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("srr_ids", nargs=-1, required=True)
def cmd_srr_to_srs(srr_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srr_to_srs(
        srrs=srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srr-to-srx", context_settings=CONTEXT_SETTINGS, help="Get SRX for a SRR")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [sample_accession (SRS),
                                        study_accession (SRP),
                                        run_alias (GSM_r),
                                        experiment_alias (GSM),
                                        sample_alias (GSM_),
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("srr_ids", nargs=-1, required=True)
def cmd_srr_to_srx(srr_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srr_to_srx(
        srrs=srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srx-to-srp", context_settings=CONTEXT_SETTINGS, help="Get SRP for a SRX")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed",
    is_flag=True,
    help="""Output additional columns: [run_accession (SRR),
                                        sample_accession (SRS),
                                        experiment_alias (GSM),
                                        run_alias (GSM_r),
                                        sample_alias (GSM),
                                        study_alias (GSE)]""",
    default=False,
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("srx_ids", nargs=-1, required=True)
def cmd_srp_to_srx(srx_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srx_to_srp(
        srxs=srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


@cli.command("srx-to-srr", context_settings=CONTEXT_SETTINGS, help="Get SRR for a SRX")
@click.option(
    "--db",
    help="Path to SRAmetadb.sqlite file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--desc", is_flag=True, help="Should sample_attribute be included", default=False
)
@click.option(
    "--detailed",
    is_flag=True,
    help="Output additional columns: [sample_accession, study_accession]",
    default=False,
)
@click.option(
    "--expand", is_flag=True, help="Should sample_attribute be expanded", default=False
)
@click.option("--saveto", help="Save output to file")
@click.argument("srx_ids", nargs=-1, required=True)
def cmd_srp_to_srr(srx_ids, db, saveto, detailed, desc, expand):
    db = _check_sradb_file(db)
    sradb = SRAdb(db)
    df = sradb.srx_to_srr(
        srxs=srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()

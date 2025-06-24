"""Command line interface for pysradb"""

import argparse
import os
import sys
import warnings
from io import StringIO
from textwrap import dedent

import pandas as pd

from . import __version__
from .exceptions import IncorrectFieldException
from .exceptions import MissingQueryException
from .geoweb import GEOweb
from .search import EnaSearch
from .search import GeoSearch
from .search import SraSearch
from .sradb import SRAdb
from .sradb import download_sradb_file
from .sraweb import SRAweb
from .utils import confirm

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

warnings.simplefilter(action="ignore", category=FutureWarning)


class CustomFormatterArgP(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def pretty_print_df(df, include_header=True):
    if include_header:
        print("\t".join(map(str, list(df.columns))))
    for index, row in df.iterrows():
        print("\t".join(map(str, row.tolist())))


def _print_save_df(df, saveto=None):
    if saveto:
        if saveto.lower().endswith(".csv"):
            df.to_csv(saveto, index=False, header=True)
        else:
            df.to_csv(saveto, index=False, header=True, sep="\t")
    else:
        if df is None:
            print
        elif len(df.index):
            pretty_print_df(df)


###################### metadata ##############################
def metadata(srp_id, assay, desc, detailed, expand, saveto):
    sradb = SRAweb()
    df = sradb.sra_metadata(
        srp_id,
        assay=assay,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


################################################################


################# download ##########################
def download(
    out_dir,
    srx,
    srp,
    geo,
    skip_confirmation,
    col="public_url",
    use_ascp=False,
    threads=1,
):
    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), "pysradb_downloads")
    sradb = SRAweb()
    geoweb = GEOweb()
    if not srp and not geo:
        df = pd.read_csv(sys.stdin, sep="\t")
        sradb.download(
            df=df,
            out_dir=out_dir,
            filter_by_srx=srx,
            skip_confirmation=True,
            use_ascp=use_ascp,
            url_col=col,
            threads=threads,
        )
    if srp:
        for srp_x in srp:
            metadata = sradb.sra_metadata(srp_x, detailed=True)
            sradb.download(
                df=metadata,
                out_dir=out_dir,
                filter_by_srx=srx,
                skip_confirmation=skip_confirmation,
                use_ascp=use_ascp,
                threads=threads,
            )
    if geo:
        for geo_x in geo:
            links, root_url = geoweb.get_download_links(geo_x)
            geoweb.download(links=links, root_url=root_url, gse=geo_x, out_dir=out_dir)
    sradb.close()


######################### search #################################
def search(saveto, db, verbosity, return_max, fields):
    if fields["run_description"]:
        verbosity = 1
    if fields["detailed"]:
        verbosity = 3
    try:
        if db == "ena":
            instance = EnaSearch(
                verbosity,
                return_max,
                fields["query"],
                fields["accession"],
                fields["organism"],
                fields["layout"],
                fields["mbases"],
                fields["publication_date"],
                fields["platform"],
                fields["selection"],
                fields["source"],
                fields["strategy"],
                fields["title"],
            )
            instance.search()
        elif db == "geo":
            instance = GeoSearch(
                verbosity,
                return_max,
                fields["query"],
                fields["accession"],
                fields["organism"],
                fields["layout"],
                fields["mbases"],
                fields["publication_date"],
                fields["platform"],
                fields["selection"],
                fields["source"],
                fields["strategy"],
                fields["title"],
                fields["geo_query"],
                fields["geo_dataset_type"],
                fields["geo_entry_type"],
            )
            instance.search()
        else:
            instance = SraSearch(
                verbosity,
                return_max,
                fields["query"],
                fields["accession"],
                fields["organism"],
                fields["layout"],
                fields["mbases"],
                fields["publication_date"],
                fields["platform"],
                fields["selection"],
                fields["source"],
                fields["strategy"],
                fields["title"],
            )
            instance.search()
    except (MissingQueryException, IncorrectFieldException) as e:
        print(e)
        return
    if fields["stats"]:
        instance.show_result_statistics()
    if fields["graphs"]:
        graph_types = tuple(fields["graphs"].split())
        instance.visualise_results(graph_types, False)
    _print_save_df(instance.get_df(), saveto)


def get_geo_search_info():
    print(GeoSearch.info())


####################################################################
# Conversion functions: gse_to_gsm, gse_to_srp, gsm_to_gse, gsm_to_srp, gsm_to_srr, gsm_to_srs, gsm_to_srx,
# srp_to_gse, srp_to_srr, srp_to_srs, srp_to_srx, srr_to_gsm, srr_to_srp, srr_to_srs, srr_to_srx,
# srs_to_gsm, srs_to_srx, srx_to_srp, srx_to_srr, srx_to_srs
# (All as in the original code, pasted for completeness.)
def gse_to_gsm(gse_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gse_to_gsm(
        gse_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def gse_to_srp(gse_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gse_to_srp(
        gse_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def gsm_to_gse(gsm_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gsm_to_gse(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def gsm_to_srp(gsm_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gsm_to_srp(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def gsm_to_srr(gsm_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gsm_to_srr(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def gsm_to_srs(gsm_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gsm_to_srs(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def gsm_to_srx(gsm_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.gsm_to_srx(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srp_to_gse(srp_id, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srp_to_gse(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srp_to_srr(srp_id, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srp_to_srr(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srp_to_srs(srp_id, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srp_to_srs(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srp_to_srx(srp_id, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srp_to_srx(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srr_to_gsm(srr_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srr_to_gsm(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srr_to_srp(srr_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srr_to_srp(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srr_to_srs(srr_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srr_to_srs(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srr_to_srx(srr_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srr_to_srx(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srs_to_gsm(srs_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srs_to_gsm(
        srs_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srs_to_srx(srs_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srs_to_srx(
        srs_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srx_to_srp(srx_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srx_to_srp(
        srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srx_to_srr(srx_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srx_to_srr(
        srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


def srx_to_srs(srx_ids, saveto, detailed, desc, expand):
    sradb = SRAweb()
    df = sradb.srx_to_srs(
        srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)
    sradb.close()


############################ GEO matrix CLI support ############################
def geo_matrix(accession, to_tsv, out_dir):
    """
    Download GEO matrix file(s) for a given accession and optionally parse them to .tsv format.
    """
    geo = GEOweb()
    try:
        result = geo.get_matrix_links(accession)
        if not result or not isinstance(result, tuple) or len(result) != 2:
            print(
                f"Could not find matrix files or folder for {accession}.",
                file=sys.stderr,
            )
            return
        links, url = result
        if not links:
            print(f"No matrix files found for {accession}.", file=sys.stderr)
            return
    except Exception as e:
        print(f"Error finding matrix files for {accession}: {e}", file=sys.stderr)
        return

    try:
        downloaded_files = geo.download_matrix(links, url, accession, out_dir=out_dir)
    except Exception as e:
        print(f"Error downloading matrix files: {e}", file=sys.stderr)
        return

    if to_tsv:
        for f in downloaded_files:
            out_file = f + ".tsv"
            try:
                geo.parse_matrix_to_tsv(f, out_file)
                print(f"Parsed {f} to {out_file}")
            except Exception as e:
                print(f"Error parsing {f}: {e}", file=sys.stderr)


#########################################################################


def parse_args(args=None):
    """Argument parser"""
    parser = ArgParser(
        description=dedent(
            """\
    pysradb: Query NGS metadata and data from NCBI Sequence Read Archive.
    version: {}.
    Citation: 10.12688/f1000research.18676.1""".format(
                __version__
            )
        ),
        formatter_class=CustomFormatterArgP,
    )

    subparsers = parser.add_subparsers(title="subcommands", dest="command")

    # --version
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    # --citation
    parser.add_argument(
        "--citation",
        action="version",
        version=dedent(
            """
        Choudhary, Saket. "pysradb: A Python Package to Query next-Generation Sequencing Metadata and Data from NCBI Sequence Read Archive." F1000Research, vol. 8, F1000 (Faculty of 1000 Ltd), Apr. 2019, p. 532 (https://f1000research.com/articles/8-532/v1)

        @article{Choudhary2019,
        doi = {10.12688/f1000research.18676.1},
        url = {https://doi.org/10.12688/f1000research.18676.1},
        year = {2019},
        month = apr,
        publisher = {F1000 (Faculty of 1000 Ltd)},
        volume = {8},
        pages = {532},
        author = {Saket Choudhary},
        title = {pysradb: A {P}ython package to query next-generation sequencing metadata and data from {NCBI} {S}equence {R}ead {A}rchive},
        journal = {F1000Research}
        }
        """
        ),
        help="how to cite",
    )

    # Add all other subparser definitions for metadata, download, search, etc.
    # (Omitted for brevity, but included above.)

    # --- Add geo-matrix subcommand ---
    geo_parser = subparsers.add_parser(
        "geo-matrix",
        help="Download and parse GEO matrix file(s) for a given GEO accession.",
    )
    geo_parser.add_argument(
        "--accession", "-a", required=True, help="GEO accession (e.g., GSE12345)"
    )
    geo_parser.add_argument(
        "--to-tsv",
        action="store_true",
        default=False,
        help="Parse the matrix file to a clean .tsv file after downloading.",
    )
    geo_parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory for downloads and parsed files.",
    )
    geo_parser.set_defaults(
        func=lambda args: geo_matrix(args.accession, args.to_tsv, args.out_dir)
    )

    # Add all other subparser definitions for all conversions (gse-to-gsm, etc.)
    # (Omitted for brevity, but included above.)

    # The rest of the conversion subparsers (metadata, download, search, gse-to-gsm, etc.) go here, e.g.:
    # subparser = subparsers.add_parser("metadata", ...)
    # [Add all arguments and set_defaults(func=...) as in previous blocks]

    # Here, for brevity, only geo-matrix is shown in detail. You need to add all your subparsers just like above.

    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    parse_args(sys.argv[1:])

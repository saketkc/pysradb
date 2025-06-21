"""Command line interface for pysradb
"""

import argparse
import os
import re
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
            #  if the save file format is csv
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
    # This block is triggered only if no -p or -g arguments are provided.
    # In this case, the input is taken from the pipe and assumed to be SRA, not GEO
    # TODO: at some point, we need to fix this
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
    # This block is triggered for downloads using the -p argument
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
    # This block is triggered for downloads using the -g argument
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


# ... all the conversion functions as in your original code
# (metadata, download, search, gse_to_gsm, gse_to_srp, gsm_to_gse, etc.)
# For brevity, I have omitted the rest of the conversion functions here but they should be included.

# --- GEO matrix CLI support ---
def geo_matrix(accession, to_tsv, out_dir):
    """
    Download GEO matrix file(s) for a given accession and optionally parse them to .tsv format.
    """
    geo = GEOweb()
    try:
        result = geo.get_matrix_links(accession)
        if not result or not isinstance(result, tuple) or len(result) != 2:
            print(f"Could not find matrix files or folder for {accession}.", file=sys.stderr)
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

    # pysradb subcommands
    subparsers = parser.add_subparsers(title="subcommands", dest="command")

    # ... all the other subparser definitions

    # pysradb geo-matrix
    subparser = subparsers.add_parser(
        "geo-matrix", help="Download and parse GEO matrix file(s) for a given GEO accession."
    )
    subparser.add_argument(
        "--accession",
        "-a",
        required=True,
        help="GEO accession (e.g., GSE12345)"
    )
    subparser.add_argument(
        "--to-tsv",
        action="store_true",
        default=False,
        help="Parse the matrix file to a clean .tsv file after downloading."
    )
    subparser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory for downloads and parsed files."
    )
    subparser.set_defaults(func=lambda args: geo_matrix(args.accession, args.to_tsv, args.out_dir))

    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    parse_args(sys.argv[1:])
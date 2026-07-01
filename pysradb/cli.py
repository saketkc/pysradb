"""Command line interface for pysradb"""

import argparse
import os
import sys
import warnings
from textwrap import dedent

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .exceptions import IncorrectFieldException, MissingQueryException
from .geoweb import GEOweb, download_geo_matrix
from .search import EnaSearch, GeoSearch, SraSearch
from .sraweb import SRAweb

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

warnings.simplefilter(action="ignore", category=FutureWarning)

console = Console()

ENRICHED_COLS = {
    "age",
    "sex",
    "ethnicity",
    "phenotype",
    "cell_type",
    "tissue",
    "strain",
    "disease",
}


class CustomFormatterArgP(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def pretty_print_df(df, include_header=True, enriched_cols=None):
    """Pretty print dataframe using rich formatting"""

    def format_value(v):
        """Convert value to string, handling None and pd.NA"""
        if v is None or pd.isna(v):
            return "[dim]-[/dim]"
        return str(v)

    if df.empty:
        console.print("[bright_black]No results found[/bright_black]")
        return

    try:
        terminal_width = console.width
    except Exception:
        terminal_width = 80  # fallback width

    num_columns = len(df.columns)
    min_col_width = 12  # minimum width per column for readability
    padding = 2  # padding between columns
    border_space = 4  # table borders

    # how many columns fit
    max_cols_per_table = (terminal_width - border_space) // (min_col_width + padding)

    # chuenk
    if num_columns > max_cols_per_table:
        console.print(
            (
                f"[bright_black]Displaying {num_columns} columns in chunks of "
                f"{max_cols_per_table}[/bright_black]"
            )
        )
        console.print()

        for i in range(0, num_columns, max_cols_per_table):
            chunk_cols = df.columns[i : i + max_cols_per_table]
            chunk_df = df[chunk_cols]

            console.print(
                f"[bright_blue]Columns {i + 1}-"
                f"{min(i + max_cols_per_table, num_columns)}:[/bright_blue]"
            )
            _create_table(
                chunk_df,
                terminal_width,
                include_header,
                format_value,
                enriched_cols,
            )
            console.print()
    else:
        _create_table(df, terminal_width, include_header, format_value, enriched_cols)


def _create_table(df, terminal_width, include_header, format_value, enriched_cols):
    """Helper function to create a rich table with appropriate sizing"""

    num_columns = len(df.columns)
    min_col_width = 12
    padding = 2
    border_space = 4

    available_width = terminal_width - border_space - (padding * (num_columns - 1))

    col_widths = []
    for column in df.columns:
        display_name = (
            f"*{column}" if enriched_cols and column in enriched_cols else str(column)
        )
        col_name = str(display_name)
        sample_data = df[column].head(10).astype(str)
        max_content_len = max(
            len(col_name), sample_data.str.len().max() if len(sample_data) > 0 else 0
        )
        col_widths.append(max_content_len)

    total_content_width = sum(col_widths)
    if total_content_width > available_width:
        scale_factor = available_width / total_content_width
        final_widths = [max(min_col_width, int(w * scale_factor)) for w in col_widths]
    else:
        final_widths = [
            max(min_col_width, min(w, available_width // num_columns + 5))
            for w in col_widths
        ]

    table = Table(
        show_header=include_header,
        header_style="bold bright_blue",
        border_style="bright_black",
        show_lines=True,
        padding=(0, 1),
        box=None,
        collapse_padding=False,
        width=terminal_width - 2,
    )

    for i, column in enumerate(df.columns):
        table.add_column(
            f"*{column}" if enriched_cols and column in enriched_cols else str(column),
            style="dim",
            no_wrap=False,
            overflow="fold",
            width=final_widths[i],
            header_style="bold bright_blue",
        )

    for index, row in df.iterrows():
        formatted_values = [format_value(v) for v in row.tolist()]
        table.add_row(*formatted_values)

    console.print(table)


def _print_save_df(df, saveto=None, enriched_cols=None):
    """Save dataframe to file or print with rich formatting.

    Automatically detects format from file extension:
    - .csv: Comma-separated values
    - .tsv: Tab-separated values
    - .txt: Tab-separated values (text format)
    - .json: JSON format
    """
    if saveto:
        file_ext = os.path.splitext(saveto)[1].lower()

        if file_ext == ".csv":
            df.to_csv(saveto, index=False, header=True)
            console.print(
                (
                    f"[bright_green]✓[/bright_green] Saved to CSV: "
                    f"[bright_blue]{saveto}[/bright_blue]"
                )
            )
        elif file_ext == ".json":
            df.to_json(saveto, orient="records", indent=2)
            console.print(
                (
                    f"[bright_green]✓[/bright_green] Saved to JSON: "
                    f"[bright_blue]{saveto}[/bright_blue]"
                )
            )
        elif file_ext in [".tsv", ".txt"]:
            df.to_csv(saveto, index=False, header=True, sep="\t")
            console.print(
                (
                    f"[bright_green]✓[/bright_green] Saved to TSV: "
                    f"[bright_blue]{saveto}[/bright_blue]"
                )
            )
        else:
            df.to_csv(saveto, index=False, header=True, sep="\t")
            console.print(
                (
                    f"[bright_green]✓[/bright_green] Saved to file: "
                    f"[bright_blue]{saveto}[/bright_blue]"
                )
            )
    else:
        if df is None:
            console.print("[bright_black]No data to display[/bright_black]")
        elif len(df.index):
            pretty_print_df(df, enriched_cols=enriched_cols)


###################### metadata ##############################
def metadata(
    srp_id,
    assay,
    desc,
    detailed,
    expand,
    saveto,
    enrich=False,
    enrich_backend=None,
    embed_model=None,
):
    # Validate that at least one ID was provided
    if not srp_id:
        console.print(
            (
                "[red]Error: No accession IDs provided. "
                "Please provide one or more SRP/GSE IDs.[/red]"
            )
        )
        console.print("[yellow]Usage: pysradb metadata SRP000001 [SRP000002 ...]")
        console.print("       pysradb metadata GSE123456[/yellow]")
        return
    if enrich and detailed:
        console.print(
            "[red]Error:[/red] --detailed cannot be used with --enrich. "
            "Enrichment uses the pysraweb API output."
        )
        return

    client = SRAweb()

    srp_ids = []
    gse_ids = []
    for accession in srp_id:
        if isinstance(accession, str) and accession.upper().startswith("GSE"):
            gse_ids.append(accession)
        else:
            srp_ids.append(accession)

    metadata_frames = []
    if srp_ids:
        try:
            srp_metadata = client.sra_metadata(
                srp_ids if len(srp_ids) > 1 else srp_ids[0],
                assay=assay,
                detailed=detailed,
                sample_attribute=desc,
                expand_sample_attributes=expand,
                enrich=enrich,
                enrich_backend=(
                    enrich_backend if enrich_backend else "ollama/granite4:3b"
                ),
                embedding_model=(
                    embed_model if embed_model else "abhinand/MedEmbed-large-v0.1"
                ),
            )
            if srp_metadata is not None:
                metadata_frames.append(srp_metadata)
        except Exception as e:
            error_msg = str(e)
            if "Failed to load model" in error_msg:
                console.print("[red]Error: Failed to load enrichment model.[/red]")
                console.print(
                    "[yellow]Please ensure the required models are installed:[/yellow]"
                )
                console.print(
                    "  1. For embedding model: pip install sentence-transformers"
                )
                # Provide LLM-specific guidance based on requested backend
                provider = (
                    enrich_backend.split("/", 1)[0] if enrich_backend else "ollama"
                )
                model_hint = (
                    enrich_backend.split("/", 1)[1]
                    if (enrich_backend and "/" in enrich_backend)
                    else "granite4:3b"
                )
                if provider == "ollama":
                    console.print("  2. For LLM: Install Ollama from https://ollama.ai")
                    console.print("     Then run: ollama serve")
                    console.print(f"     Then pull the model: ollama pull {model_hint}")
                elif provider == "lmstudio":
                    console.print(
                        "  2. For LLM: Ensure LM Studio is installed and running"
                    )
                    console.print(
                        "     Consult LM Studio docs for pulling or registering models."
                    )
                else:
                    console.print(
                        (
                            f"  2. For LLM: Ensure {provider} backend is available "
                            "and the model is installed"
                        )
                    )
                return
            elif "connect" in error_msg.lower() or "connection" in error_msg.lower():
                provider = (
                    enrich_backend.split("/", 1)[0] if enrich_backend else "ollama"
                )
                model_hint = (
                    enrich_backend.split("/", 1)[1]
                    if (enrich_backend and "/" in enrich_backend)
                    else "granite4:3b"
                )
                if provider == "ollama":
                    console.print(
                        "[red]Error: Cannot connect to Ollama server "
                        "or load model.[/red]"
                    )
                    console.print(
                        "[yellow]Please ensure Ollama is installed "
                        "and running:[/yellow]"
                    )
                    console.print("  1. Install Ollama from https://ollama.ai")
                    console.print("  2. Start Ollama: ollama serve")
                    console.print(f"  3. Pull the model: ollama pull {model_hint}")
                elif provider == "lmstudio":
                    console.print(
                        "[red]Error: Cannot connect to LM Studio or load model.[/red]"
                    )
                    console.print(
                        (
                            "[yellow]Please ensure LM Studio is running and the "
                            "model is available."
                            "[/yellow]"
                        )
                    )
                    console.print("  1. Check LM Studio documentation for model setup")
                else:
                    console.print(
                        f"[red]Error: Cannot connect to {provider} backend "
                        "or load model.[/red]"
                    )
                    console.print(
                        "[yellow]Please ensure the backend/service is running "
                        "and the requested model is available.[/yellow]"
                    )
                return
            elif "enrichment" in error_msg.lower():
                console.print("[red]Error: Metadata enrichment failed.[/red]")
                console.print(f"[yellow]Details: {error_msg}[/yellow]")
                return
            else:
                raise

    if gse_ids:
        try:
            geo_metadata_df = client.geo_metadata(
                gse_ids if len(gse_ids) > 1 else gse_ids[0],
                sample_attribute=desc,
                detailed=detailed,
                enrich=enrich,
                enrich_backend=(
                    enrich_backend if enrich_backend else "ollama/granite4:3b"
                ),
                embedding_model=(
                    embed_model if embed_model else "abhinand/MedEmbed-large-v0.1"
                ),
            )
            if not geo_metadata_df.empty:
                metadata_frames.append(geo_metadata_df)
        except Exception as e:
            error_msg = str(e)
            if "Failed to load model" in error_msg:
                console.print("[red]Error: Failed to load enrichment model.[/red]")
                console.print(
                    "[yellow]Please ensure the required models are installed:[/yellow]"
                )
                console.print(
                    "  1. For embedding model: pip install sentence-transformers"
                )
                provider = (
                    enrich_backend.split("/", 1)[0] if enrich_backend else "ollama"
                )
                model_hint = (
                    enrich_backend.split("/", 1)[1]
                    if (enrich_backend and "/" in enrich_backend)
                    else "granite4:3b"
                )
                if provider == "ollama":
                    console.print("  2. For LLM: Install Ollama from https://ollama.ai")
                    console.print("     Then run: ollama serve")
                    console.print(f"     Then pull the model: ollama pull {model_hint}")
                elif provider == "lmstudio":
                    console.print(
                        "  2. For LLM: Ensure LM Studio is installed and running"
                    )
                    console.print(
                        "     Consult LM Studio docs for pulling or registering models."
                    )
                else:
                    console.print(
                        f"  2. For LLM: Ensure {provider} backend is available "
                        "and the model is installed"
                    )
                return
            elif "connect" in error_msg.lower() or "connection" in error_msg.lower():
                provider = (
                    enrich_backend.split("/", 1)[0] if enrich_backend else "ollama"
                )
                model_hint = (
                    enrich_backend.split("/", 1)[1]
                    if (enrich_backend and "/" in enrich_backend)
                    else "granite4:3b"
                )
                if provider == "ollama":
                    console.print(
                        "[red]Error: Cannot connect to Ollama server "
                        "or load model.[/red]"
                    )
                    console.print(
                        "[yellow]Please ensure Ollama is installed "
                        "and running:[/yellow]"
                    )
                    console.print("  1. Install Ollama from https://ollama.ai")
                    console.print("  2. Start Ollama: ollama serve")
                    console.print(f"  3. Pull the model: ollama pull {model_hint}")
                elif provider == "lmstudio":
                    console.print(
                        "[red]Error: Cannot connect to LM Studio or load model.[/red]"
                    )
                    console.print(
                        "[yellow]Please ensure LM Studio is running "
                        "and the model is available.[/yellow]"
                    )
                    console.print("  1. Check LM Studio documentation for model setup")
                else:
                    console.print(
                        f"[red]Error: Cannot connect to {provider} backend "
                        "or load model.[/red]"
                    )
                    console.print(
                        "[yellow]Please ensure the backend/service is running "
                        "and the requested model is available.[/yellow]"
                    )
                return
            elif "enrichment" in error_msg.lower():
                console.print("[red]Error: Metadata enrichment failed.[/red]")
                console.print(f"[yellow]Details: {error_msg}[/yellow]")
                return
            else:
                raise

    if metadata_frames:
        df = pd.concat(metadata_frames, ignore_index=True, sort=False)
    else:
        df = pd.DataFrame()

    _print_save_df(df, saveto, enriched_cols=ENRICHED_COLS if enrich else None)


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
    client = SRAweb()
    geoweb = GEOweb()
    # This block is triggered only if no -p or -g arguments are provided.
    # In this case, the input is taken from the pipe and assumed to be SRA, not GEO
    # TODO: at some point, we need to fix this
    if not srp and not geo:
        df = pd.read_csv(sys.stdin, sep="\t")
        client.download(
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
            metadata = client.sra_metadata(srp_x, detailed=True)
            client.download(
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


#########################################################


######################### search #################################
def search(saveto, db, verbosity, return_max, fields, return_df=False):
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
        console.print(f"[bright_red]Error:[/bright_red] {e}")
        return
    if fields["stats"]:
        instance.show_result_statistics()
    if fields["graphs"]:
        graph_types = tuple(fields["graphs"].split())
        instance.visualise_results(graph_types, False)
    if return_df:
        return instance.get_df()
    else:
        _print_save_df(instance.get_df(), saveto)


def get_geo_search_info():
    info_text = GeoSearch.info()
    panel = Panel(
        info_text,
        title="[bold bright_blue]GeoSearch Information[/bold bright_blue]",
        border_style="bright_blue",
        padding=(1, 2),
    )
    console.print(panel)


####################################################################


######################### gse-to-gsm ###############################
def gse_to_gsm(gse_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gse_to_gsm(
        gse_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


####################################################################


######################## gse-to-srp ################################
def gse_to_srp(gse_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gse_to_srp(
        gse_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


######################################################################


######################### gsm-to-gse #################################
def gsm_to_gse(gsm_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gsm_to_gse(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


########################################################################


############################ gsm-to-srp ################################
def gsm_to_srp(gsm_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gsm_to_srp(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


########################################################################


############################ gsm-to-srr ################################
def gsm_to_srr(gsm_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gsm_to_srr(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


########################################################################


############################ gsm-to-srs ################################
def gsm_to_srs(gsm_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gsm_to_srs(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


########################################################################


############################# gsm-to-srx ###############################
def gsm_to_srx(gsm_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.gsm_to_srx(
        gsm_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srp-to-gse ##################################
def srp_to_gse(srp_id, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srp_to_gse(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srp-to-srr ##################################
def srp_to_srr(srp_id, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srp_to_srr(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srp-to-srs ##################################
def srp_to_srs(srp_id, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srp_to_srs(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srp-to-srx ##################################
def srp_to_srx(srp_id, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srp_to_srx(
        srp_id,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srr-to-gsm ##################################
def srr_to_gsm(srr_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srr_to_gsm(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


########################################################################


########################### srr-to-srp ##################################
def srr_to_srp(srr_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srr_to_srp(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srr-to-srs ##################################
def srr_to_srs(srr_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srr_to_srs(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srr-to-srx ##################################
def srr_to_srx(srr_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srr_to_srx(
        srr_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srs-to-gsm ##################################
def srs_to_gsm(srs_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srs_to_gsm(
        srs_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srs-to-srx ##################################
def srs_to_srx(srs_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srs_to_srx(
        srs_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srx-to-srp ##################################
def srx_to_srp(srx_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srx_to_srp(
        srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srx-to-srr ##################################
def srx_to_srr(srx_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srx_to_srr(
        srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


#########################################################################


########################### srx-to-srs ##################################
def srx_to_srs(srx_ids, saveto, detailed, desc, expand):
    client = SRAweb()
    df = client.srx_to_srs(
        srx_ids,
        detailed=detailed,
        sample_attribute=desc,
        expand_sample_attributes=expand,
    )
    _print_save_df(df, saveto)


def srp_to_pmid(srp_ids, saveto, detailed=False):
    client = SRAweb()
    df = client.srp_to_pmid(srp_ids, detailed=detailed)
    _print_save_df(df, saveto)


def sra_to_pmid(sra_ids, saveto):
    """Backward compatibility wrapper for sra_to_pmid"""
    client = SRAweb()
    df = client.sra_to_pmid(sra_ids)
    _print_save_df(df, saveto)


def gse_to_pmid(gse_ids, saveto, detailed=False):
    client = SRAweb()
    df = client.gse_to_pmid(gse_ids, detailed=detailed)
    _print_save_df(df, saveto)


def pmid_info(ids, saveto, detailed=False):
    client = SRAweb()
    df = client.pmid_info(ids, detailed=detailed)
    _print_save_df(df, saveto)


def ae_to_pmid(ae_ids, saveto):
    client = SRAweb()
    df = client.ae_to_pmid(ae_ids)
    _print_save_df(df, saveto)


def ena_to_pmid(ena_ids, saveto):
    client = SRAweb()
    df = client.ena_to_pmid(ena_ids)
    _print_save_df(df, saveto)


def pmid_to_gse(pmid_ids, saveto, retries=3):
    client = SRAweb()
    df = client.pmid_to_gse(pmid_ids, retries=retries)
    _print_save_df(df, saveto)


def pmid_to_srp(pmid_ids, saveto, retries=3):
    client = SRAweb()
    df = client.pmid_to_srp(pmid_ids, retries=retries)
    _print_save_df(df, saveto)


def pmc_to_identifiers(pmc_ids, saveto, retries=3):
    client = SRAweb()
    df = client.pmc_to_identifiers(pmc_ids, retries=retries)
    _print_save_df(df, saveto)


def pmid_to_identifiers(pmid_ids, saveto, retries=3):
    client = SRAweb()
    df = client.pmid_to_identifiers(pmid_ids, retries=retries)
    _print_save_df(df, saveto)


def doi_to_gse(doi_ids, saveto):
    client = SRAweb()
    df = client.doi_to_gse(doi_ids)
    _print_save_df(df, saveto)


def doi_to_srp(doi_ids, saveto):
    client = SRAweb()
    df = client.doi_to_srp(doi_ids)
    _print_save_df(df, saveto)


def doi_to_identifiers(doi_ids, saveto):
    client = SRAweb()
    df = client.doi_to_identifiers(doi_ids)
    _print_save_df(df, saveto)


#########################################################################


########################### geo-matrix ##################################
def geo_matrix(accession, to_tsv, output_dir):
    # Download the GEO Matrix file
    matrix_file = download_geo_matrix(accession, output_dir=output_dir)
    console.print(
        f"[bright_green]✓[/bright_green] Downloaded GEO Matrix file to: "
        f"[bright_blue]{matrix_file}[/bright_blue]"
    )

    # If --to-tsv is specified, parse the file to TSV
    if to_tsv:
        output_tsv = os.path.join(output_dir, f"{accession}_matrix.tsv")
        # df = parse_geo_matrix_to_tsv(matrix_file, output_tsv)
        console.print(
            f"[bright_green]✓[/bright_green] Parsed GEO Matrix file to TSV: "
            f"[bright_blue]{output_tsv}[/bright_blue]"
        )


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

    # pysradb subcommands
    subparsers = parser.add_subparsers(title="subcommands", dest="command")

    # pysradb --version
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    # pysradb --citation
    parser.add_argument(
        "--citation",
        action="version",
        version=dedent(
            """
        Choudhary, Saket. "pysradb: A Python Package to Query next-Generation Sequencing
        Metadata and Data from NCBI Sequence Read Archive."
        F1000Research, vol. 8, F1000 (Faculty of 1000 Ltd), Apr. 2019, p. 532
        (https://f1000research.com/articles/8-532/v1)

        @article{Choudhary2019,
        doi = {10.12688/f1000research.18676.1},
        url = {https://doi.org/10.12688/f1000research.18676.1},
        year = {2019},
        month = apr,
        publisher = {F1000 (Faculty of 1000 Ltd)},
        volume = {8},
        pages = {532},
        author = {Saket Choudhary},
        title = {pysradb: A {P}ython package to query next-generation sequencing
        metadata and data from {NCBI} {S}equence {R}ead {A}rchive},
        journal = {F1000Research}
        }
        """
        ),
        help="how to cite",
    )

    # pysradb metadata
    subparser = subparsers.add_parser(
        "metadata", help="Fetch metadata for SRA project (SRPnnnn)"
    )
    subparser.add_argument("--saveto", help="Save metadata dataframe to file")
    subparser.add_argument(
        "--assay", action="store_true", help="Include assay type in output"
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed", action="store_true", help="Display detailed metadata table"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument(
        "--enrich",
        action="store_true",
        help="Enrich metadata with standardized biological attributes using LLMs",
    )
    subparser.add_argument(
        "--model",
        dest="enrich_backend",
        type=str,
        default=None,
        help="LLM model for enrichment (e.g., 'ollama/granite4:3b', 'ollama/llama3.2'). "
        "If not specified, uses default backend",
    )
    subparser.add_argument(
        "--embed-model",
        dest="embed_model",
        type=str,
        default=None,
        help=(
            "Embedding model for enrichment (e.g., "
            "'abhinand/MedEmbed-large-v0.1'). If not specified, uses default"
        ),
    )
    subparser.add_argument("srp_id", nargs="+")
    subparser.set_defaults(func=metadata)

    # pysradb download
    subparser = subparsers.add_parser("download", help="Download SRA project (SRPnnnn)")
    subparser.add_argument("--out-dir", help="Output directory root")
    subparser.add_argument("--srx", "-x", help="Download only these SRX(s)", nargs="+")
    subparser.add_argument("--srp", "-p", help="SRP ID", nargs="+")
    subparser.add_argument("--geo", "-g", help="GEO ID", nargs="+")
    subparser.add_argument(
        "--skip-confirmation", "-y", action="store_true", help="Skip confirmation"
    )
    subparser.add_argument(
        "--use_ascp", "-a", action="store_true", help="Use aspera instead of wget"
    )
    subparser.add_argument(
        "--col", help="Specify column to download", default="public_url"
    )
    subparser.add_argument(
        "--threads", "-t", help="Number of threads", default=1, type=int
    )
    subparser.set_defaults(func=download)

    # pysradb search
    subparser = subparsers.add_parser("search", help="Search SRA/ENA for matching text")
    subparser.add_argument(
        "-o", "--saveto", help="Save search result dataframe to file"
    )
    subparser.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="Displays some useful statistics for the search results.",
    )
    subparser.add_argument(
        "-g",
        "--graphs",
        nargs="?",
        const="all",
        help=(
            "Generates graphs to illustrate the search result. "
            "By default all graphs are generated. \n"
            "Alternatively, select a subset from the options below "
            "in a space-separated string:\n"
            "daterange, organism, source, selection, platform, basecount"
        ),
    )
    subparser.add_argument(
        "-d",
        "--db",
        choices=["ena", "geo", "sra"],
        default="sra",
        help="Select the db API (sra, ena, or geo) to query, default = sra.     "
        "Note: pysradb search works slightly differently when db = geo. \n"
        "Please refer to 'pysradb search --geo-info' for more details.",
    )
    subparser.add_argument(
        "-v",
        "--verbosity",
        choices=[0, 1, 2, 3],
        default=2,
        help=(
            "Level of search result details (0, 1, 2 or 3), default = 2\n"
            "0: run accession only\n"
            "1: run accession and experiment title\n"
            "2: accession numbers, titles and sequencing information\n"
            "3: records in 2 and other information such as download url, "
            "sample attributes, etc"
        ),
        type=int,
    )
    subparser.add_argument(
        "--run-description",
        action="store_true",
        help="Displays run accessions and descriptions only. "
        "Equivalent to --verbosity 1",
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Displays detailed search results. Equivalent to --verbosity 3.",
    )
    subparser.add_argument(
        "-m",
        "--max",
        default=20,
        help="Maximum number of entries to return, default = 20",
        type=int,
    )
    subparser.add_argument(
        "-q",
        "--query",
        nargs="+",
        help=(
            "Main query string. Note that if no query is supplied, at least one of the "
            "following flags must be present:"
        ),
    )
    subparser.add_argument("-A", "--accession", help="Accession number")
    subparser.add_argument(
        "-O", "--organism", nargs="+", help="Scientific name of the sample organism"
    )
    subparser.add_argument(
        "-L",
        "--layout",
        choices=["SINGLE", "PAIRED"],
        help="Library layout. Accepts either SINGLE or PAIRED",
        type=str.upper,
    )
    subparser.add_argument(
        "-M",
        "--mbases",
        help="Size of the sample rounded to the nearest megabase",
        type=int,
    )
    subparser.add_argument(
        "-D",
        "--publication-date",
        help=(
            "Publication date of the run in the format dd-mm-yyyy. "
            "If a date range is desired, enter the start date, followed by end date, "
            "separated by a colon ':'.\n Example: 01-01-2010:31-12-2010"
        ),
    )
    subparser.add_argument("-P", "--platform", nargs="+", help="Sequencing platform")
    subparser.add_argument("-E", "--selection", nargs="+", help="Library selection")
    subparser.add_argument("-C", "--source", nargs="+", help="Library source")
    subparser.add_argument(
        "-S", "--strategy", nargs="+", help="Library preparation strategy"
    )
    subparser.add_argument("-T", "--title", nargs="+", help="Experiment title")

    # The following arguments are for GEO DataSets only
    subparser.add_argument(
        "-I",
        "--geo-info",
        action="store_true",
        help=(
            "Displays information on how to query GEO DataSets via "
            "'pysradb search --db geo ...', "
            "including accepted inputs for -G/--geo-query, -Y/--geo-dataset-type "
            "and -Z/--geo-entry-type. "
        ),
    )
    subparser.add_argument(
        "-G",
        "--geo-query",
        nargs="+",
        help=(
            "Main query string for GEO DataSet. "
            "This flag is only used when db is set to be geo."
            "Please refer to 'pysradb search --geo-info' for more details."
        ),
    )
    subparser.add_argument(
        "-Y",
        "--geo-dataset-type",
        nargs="+",
        help="GEO DataSet Type. This flag is only used when --db is set to be geo."
        "Please refer to 'pysradb search --geo-info' for more details.",
    )
    subparser.add_argument(
        "-Z",
        "--geo-entry-type",
        nargs="+",
        help="GEO Entry Type. This flag is only used when --db is set to be geo."
        "Please refer to 'pysradb search --geo-info' for more details.",
    )

    subparser.set_defaults(func=search)

    # pysradb gse-to-gsm
    subparser = subparsers.add_parser("gse-to-gsm", help="Get GSM for a GSE")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [sample_accession (SRS),
                                         run_accession (SRR),
                                         sample_alias (GSM),
                                         run_alias (GSM_r)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("gse_ids", nargs="+")
    subparser.set_defaults(func=gse_to_gsm)

    # pysradb gse-to-srp
    subparser = subparsers.add_parser("gse-to-srp", help="Get SRP for a GSE")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [experiment_accession (SRX),
                                           run_accession (SRR),
                                           sample_accession (SRS),
                                           experiment_alias (GSM_),
                                           run_alias (GSM_r),
                                           sample_alias (GSM)]
                                           """,
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("gse_ids", nargs="+")
    subparser.set_defaults(func=gse_to_srp)

    # pysradb gsm-to-gse
    subparser = subparsers.add_parser("gsm-to-gse", help="Get GSE for a GSM")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [sample_accession (SRS),
                                            run_accession (SRR),
                                            sample_alias (GSM),
                                            run_alias (GSM_r)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("gsm_ids", nargs="+")
    subparser.set_defaults(func=gsm_to_gse)

    # pysradb gsm-to-srp
    subparser = subparsers.add_parser("gsm-to-srp", help="Get SRP for a GSM")
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [experiment_accession (SRX),
                                            sample_accession (SRS),
                                            run_accession (SRR),
                                            experiment_alias (GSM),
                                            sample_alias (GSM),
                                            run_alias (GSM_r),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("gsm_ids", nargs="+")
    subparser.set_defaults(func=gsm_to_srp)

    # pysradb gsm-to-srr
    subparser = subparsers.add_parser("gsm-to-srr", help="Get SRR for a GSM")
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [experiment_accession (SRX),
                                            sample_accession (SRS),
                                            study_accession (SRP),
                                            run_alias (GSM_r),
                                            sample_alias (GSM),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("gsm_ids", nargs="+")
    subparser.set_defaults(func=gsm_to_srr)

    # pysradb gsm-to-srs
    subparser = subparsers.add_parser("gsm-to-srs", help="Get SRS for a GSM")
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [experiment_accession (SRX),
                                            run_accession (SRR),
                                            study_accession (SRP),
                                            run_alias (GSM_r),
                                            experiment_alias (GSM),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("gsm_ids", nargs="+")
    subparser.set_defaults(func=gsm_to_srs)

    # pysradb gsm-to-srx
    subparser = subparsers.add_parser("gsm-to-srx", help="Get SRX for a GSM")
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [experiment_accession (SRX),
                                            sample_accession (SRS),
                                            run_accession (SRR),
                                            experiment_alias (GSM),
                                            sample_alias (GSM),
                                            run_alias (GSM_r),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("gsm_ids", nargs="+")
    subparser.set_defaults(func=gsm_to_srx)

    # pysradb srp-to-gse
    subparser = subparsers.add_parser("srp-to-gse", help="Get GSE for a SRP")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Output additional columns: [sample_accession, run_accession]",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srp_id")
    subparser.set_defaults(func=srp_to_gse)

    # pysradb srp-to-srr
    subparser = subparsers.add_parser("srp-to-srr", help="Get SRR for a SRP")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [experiment_accession (SRX),
                                            sample_accession (SRS),
                                            study_alias (GSE),
                                            experiment_alias (GSM),
                                            sample_alias (GSM_),
                                            run_alias (GSM_r)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srp_id")
    subparser.set_defaults(func=srp_to_srr)

    # pysradb srp-to-srs
    subparser = subparsers.add_parser("srp-to-srs", help="Get SRS for a SRP")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [run_accession (SRR),
                                            study_accession (SRP),
                                            experiment_alias (GSM),
                                            sample_alias (GSM_),
                                            run_alias (GSM_r),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srp_id")
    subparser.set_defaults(func=srp_to_srs)

    # pysradb srp-to-srx
    subparser = subparsers.add_parser("srp-to-srx", help="Get SRX for a SRP")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [sample_accession (SRS),
                                            run_accession (SRR),
                                            experiment_alias (GSM),
                                            sample_alias (GSM_),
                                            run_alias (GSM_r)',
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srp_id")
    subparser.set_defaults(func=srp_to_srx)

    # pysradb srr-to-gsm
    subparser = subparsers.add_parser("srr-to-gsm", help="Get GSM for a SRR")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""'Output additional columns: [experiment_accession (SRX),
                                             study_accession (SRP),
                                             run_alias (GSM_r),
                                             sample_alias (GSM_),
                                             experiment_alias (GSM),
                                             study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("srr_ids", nargs="+")
    subparser.set_defaults(func=srr_to_gsm)

    # pysradb srr-to-srp
    subparser = subparsers.add_parser("srr-to-srp", help="Get SRP for a SRR")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""'Output additional columns: [experiment_accession (SRX),
                                             sample_accession (SRS),
                                             run_alias (GSM_r),
                                             experiment_alias (GSM),
                                             sample_alias (GSM_),
                                             study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("srr_ids", nargs="+")
    subparser.set_defaults(func=srr_to_srp)

    # pysradb srr-to-srs
    subparser = subparsers.add_parser("srr-to-srs", help="Get SRS for a SRR")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""'Output additional columns: [experiment_accession (SRX),
                                             study_accession (SRP),
                                             run_alias (GSM_r),
                                             sample_alias (GSM_),
                                             experiment_alias (GSM),
                                             study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("srr_ids", nargs="+")
    subparser.set_defaults(func=srr_to_srs)

    # pysradb srr-to-srx
    subparser = subparsers.add_parser("srr-to-srx", help="Get SRX for a SRR")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [sample_accession (SRS),
                                            study_accession (SRP),
                                            run_alias (GSM_r),
                                            experiment_alias (GSM),
                                            sample_alias (GSM_),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("srr_ids", nargs="+")
    subparser.set_defaults(func=srr_to_srx)

    # pysradb srs-to-gsm
    subparser = subparsers.add_parser("srs-to-gsm", help="Get GSM for a SRS")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Output additional columns: [run_accession, study_accession]",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srs_ids", nargs="+")
    subparser.set_defaults(func=srs_to_gsm)

    # pysradb srs-to-srx
    subparser = subparsers.add_parser("srs-to-srx", help="Get SRX for a SRS")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Output additional columns: [run_accession, study_accession]",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srs_ids", nargs="+")
    subparser.set_defaults(func=srs_to_srx)

    # pysradb srx-to-srp
    subparser = subparsers.add_parser("srx-to-srp", help="Get SRP for a SRX")
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="""Output additional columns: [run_accession (SRR),
                                            sample_accession (SRS),
                                            experiment_alias (GSM),
                                            run_alias (GSM_r),
                                            sample_alias (GSM),
                                            study_alias (GSE)]""",
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("srx_ids", nargs="+")
    subparser.set_defaults(func=srx_to_srp)

    # pysradb srx-to-srr
    subparser = subparsers.add_parser("srx-to-srr", help="Get SRR for a SRX")
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Output additional columns: [sample_accession, study_accession]",
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("srx_ids", nargs="+")
    subparser.set_defaults(func=srx_to_srr)

    # pysradb srx-to-srs
    subparser = subparsers.add_parser("srx-to-srs", help="Get SRS for a SRX")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Output additional columns: [run_accession, study_accession]",
    )
    subparser.add_argument(
        "--desc", action="store_true", help="Should sample_attribute be included"
    )
    subparser.add_argument(
        "--expand", action="store_true", help="Should sample_attribute be expanded"
    )
    subparser.add_argument("srx_ids", nargs="+")
    subparser.set_defaults(func=srx_to_srs)

    # pysradb geo-matrix
    subparser = subparsers.add_parser(
        "geo-matrix", help="Download and parse GEO Matrix files"
    )
    subparser.add_argument(
        "--accession", required=True, help="GEO accession (e.g., GSE234190)"
    )
    subparser.add_argument(
        "--to-tsv", action="store_true", help="Convert the matrix file to TSV format"
    )
    subparser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)",
    )
    subparser.set_defaults(func=geo_matrix)

    # pysradb srp-to-pmid
    subparser = subparsers.add_parser(
        "srp-to-pmid", help="Get PMIDs for SRP accessions"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Include publication metadata (title, journal, DOI, pub_date, authors)",
    )
    subparser.add_argument("srp_ids", nargs="+", help="SRP accession(s)")
    subparser.set_defaults(func=srp_to_pmid)

    # pysradb gse-to-pmid
    subparser = subparsers.add_parser(
        "gse-to-pmid", help="Get PMIDs for GSE accessions"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Include publication metadata (title, journal, DOI, pub_date, authors)",
    )
    subparser.add_argument("gse_ids", nargs="+", help="GSE accession(s)")
    subparser.set_defaults(func=gse_to_pmid)

    # pysradb ae-to-pmid
    subparser = subparsers.add_parser(
        "ae-to-pmid", help="Get PMIDs for ArrayExpress accessions"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("ae_ids", nargs="+", help="ArrayExpress accession(s)")
    subparser.set_defaults(func=ae_to_pmid)

    # pysradb ena-to-pmid
    subparser = subparsers.add_parser(
        "ena-to-pmid", help="Get PMIDs for ENA/BioProject accessions"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "ena_ids", nargs="+", help="ENA accession(s) (PRJEB/PRJNA/PRJD)"
    )
    subparser.set_defaults(func=ena_to_pmid)

    # pysradb pmid-info
    subparser = subparsers.add_parser(
        "pmid-info",
        help="Get publication metadata and journal metrics for PMIDs, PMCIDs, or DOIs",
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--detailed",
        action="store_true",
        help="Also look up associated GEO/SRA datasets",
    )
    subparser.add_argument("ids", nargs="+", help="PMID(s), PMCID(s), or DOI(s)")
    subparser.set_defaults(func=pmid_info)

    # pysradb pmid-to-gse
    subparser = subparsers.add_parser(
        "pmid-to-gse", help="Get GSE accessions from PMIDs"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of additional retries for failed PubMed/PMC requests",
    )
    subparser.add_argument("pmid_ids", nargs="+", help="PMID(s)")
    subparser.set_defaults(func=pmid_to_gse)

    # pysradb pmid-to-srp
    subparser = subparsers.add_parser(
        "pmid-to-srp", help="Get SRP accessions from PMIDs"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of additional retries for failed PubMed/PMC requests",
    )
    subparser.add_argument("pmid_ids", nargs="+", help="PMID(s)")
    subparser.set_defaults(func=pmid_to_srp)

    # pysradb pmc-to-identifiers
    subparser = subparsers.add_parser(
        "pmc-to-identifiers", help="Extract database identifiers from PMC articles"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of additional retries for failed PMC full-text requests",
    )
    subparser.add_argument("pmc_ids", nargs="+", help="PMC ID(s)")
    subparser.set_defaults(func=pmc_to_identifiers)

    # pysradb pmid-to-identifiers
    subparser = subparsers.add_parser(
        "pmid-to-identifiers", help="Extract database identifiers from PubMed articles"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of additional retries for failed PubMed/PMC requests",
    )
    subparser.add_argument("pmid_ids", nargs="+", help="PMID(s)")
    subparser.set_defaults(func=pmid_to_identifiers)

    # pysradb doi-to-gse
    subparser = subparsers.add_parser("doi-to-gse", help="Get GSE accessions from DOIs")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("doi_ids", nargs="+", help="DOI(s)")
    subparser.set_defaults(func=doi_to_gse)

    # pysradb doi-to-srp
    subparser = subparsers.add_parser("doi-to-srp", help="Get SRP accessions from DOIs")
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("doi_ids", nargs="+", help="DOI(s)")
    subparser.set_defaults(func=doi_to_srp)

    # pysradb doi-to-identifiers
    subparser = subparsers.add_parser(
        "doi-to-identifiers", help="Extract database identifiers from articles via DOI"
    )
    subparser.add_argument("--saveto", help="Save output to file")
    subparser.add_argument("doi_ids", nargs="+", help="DOI(s)")
    subparser.set_defaults(func=doi_to_identifiers)

    parsed_args = args if args is not None else (None if sys.argv[1:] else ["--help"])
    args = parser.parse_args(parsed_args)
    if args.command == "metadata":
        if args.enrich:
            backend = (
                args.enrich_backend if args.enrich_backend else "ollama/granite4:3b"
            )
            console.print(
                f"Enriching metadata with {backend.replace(':', '-')}",
                style="green",
            )
        metadata(
            args.srp_id,
            args.assay,
            args.desc,
            args.detailed,
            args.expand,
            args.saveto,
            args.enrich,
            args.enrich_backend,
            args.embed_model,
        )
    elif args.command == "download":
        download(
            args.out_dir,
            args.srx,
            args.srp,
            args.geo,
            args.skip_confirmation,
            args.col,
            args.use_ascp,
            args.threads,
        )
    elif args.command == "search":
        flags = vars(args)
        if flags.pop("geo_info"):
            get_geo_search_info()
        else:
            search(
                flags.pop("saveto"),
                flags.pop("db"),
                flags.pop("verbosity"),
                flags.pop("max"),
                flags,
            )
    elif args.command == "gse-to-gsm":
        gse_to_gsm(args.gse_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "gse-to-srp":
        gse_to_srp(args.gse_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "gsm-to-gse":
        gsm_to_gse(args.gsm_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "gsm-to-srp":
        gsm_to_srp(args.gsm_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "gsm-to-srr":
        gsm_to_srr(args.gsm_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "gsm-to-srs":
        gsm_to_srs(args.gsm_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "gsm-to-srx":
        gsm_to_srx(args.gsm_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srp-to-gse":
        srp_to_gse(args.srp_id, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srp-to-srr":
        srp_to_srr(args.srp_id, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srp-to-srs":
        srp_to_srs(args.srp_id, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srp-to-srx":
        srp_to_srx(args.srp_id, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srr-to-gsm":
        srr_to_gsm(args.srr_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srr-to-srp":
        srr_to_srp(args.srr_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srr-to-srs":
        srr_to_srs(args.srr_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srr-to-srx":
        srr_to_srx(args.srr_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srs-to-gsm":
        srs_to_gsm(args.srs_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srs-to-srx":
        srs_to_srx(args.srs_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srx-to-srp":
        srx_to_srp(args.srx_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srx-to-srr":
        srx_to_srr(args.srx_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "srx-to-srs":
        srx_to_srs(args.srx_ids, args.saveto, args.detailed, args.desc, args.expand)
    elif args.command == "geo-matrix":
        geo_matrix(args.accession, args.to_tsv, args.output_dir)
    elif args.command == "srp-to-pmid":
        srp_to_pmid(args.srp_ids, args.saveto, args.detailed)
    elif args.command == "gse-to-pmid":
        gse_to_pmid(args.gse_ids, args.saveto, args.detailed)
    elif args.command == "ae-to-pmid":
        ae_to_pmid(args.ae_ids, args.saveto)
    elif args.command == "ena-to-pmid":
        ena_to_pmid(args.ena_ids, args.saveto)
    elif args.command == "pmid-info":
        pmid_info(args.ids, args.saveto, args.detailed)
    elif args.command == "pmid-to-gse":
        pmid_to_gse(args.pmid_ids, args.saveto, args.retries)
    elif args.command == "pmid-to-srp":
        pmid_to_srp(args.pmid_ids, args.saveto, args.retries)
    elif args.command == "pmc-to-identifiers":
        pmc_to_identifiers(args.pmc_ids, args.saveto, args.retries)
    elif args.command == "pmid-to-identifiers":
        pmid_to_identifiers(args.pmid_ids, args.saveto, args.retries)
    elif args.command == "doi-to-gse":
        doi_to_gse(args.doi_ids, args.saveto)
    elif args.command == "doi-to-srp":
        doi_to_srp(args.doi_ids, args.saveto)
    elif args.command == "doi-to-identifiers":
        doi_to_identifiers(args.doi_ids, args.saveto)


if __name__ == "__main__":
    parse_args(sys.argv[1:])

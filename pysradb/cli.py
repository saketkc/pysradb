import click
from .geoweb import GEOweb

@click.group()
def cli():
    pass

@cli.command(
    "geo-matrix",
    short_help="Download and parse GEO matrix file(s) for a given GEO accession."
)
@click.option(
    "--accession",
    "-a",
    required=True,
    help="GEO accession (e.g., GSE12345)"
)
@click.option(
    "--to-tsv",
    is_flag=True,
    default=False,
    help="Parse the matrix file to a clean .tsv file after downloading."
)
@click.option(
    "--out-dir",
    default=None,
    help="Output directory for downloads and parsed files."
)
def geo_matrix(accession, to_tsv, out_dir):
    """
    Download GEO matrix file(s) for a given accession and optionally parse them to .tsv format.
    """
    geo = GEOweb()
    try:
        result = geo.get_matrix_links(accession)
        if not result or not isinstance(result, tuple) or len(result) != 2:
            click.echo(f"Could not find matrix files or folder for {accession}.", err=True)
            return
        links, url = result
        if not links:
            click.echo(f"No matrix files found for {accession}.", err=True)
            return
    except Exception as e:
        click.echo(f"Error finding matrix files for {accession}: {e}", err=True)
        return

    try:
        downloaded_files = geo.download_matrix(links, url, accession, out_dir=out_dir)
    except Exception as e:
        click.echo(f"Error downloading matrix files: {e}", err=True)
        return

    if to_tsv:
        for f in downloaded_files:
            out_file = f + ".tsv"
            try:
                geo.parse_matrix_to_tsv(f, out_file)
                click.echo(f"Parsed {f} to {out_file}")
            except Exception as e:
                click.echo(f"Error parsing {f}: {e}", err=True)

if __name__ == "__main__":
    cli()
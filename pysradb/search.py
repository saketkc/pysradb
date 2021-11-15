"""This file contains the search classes for the search feature.
"""
import os
import re
import sys
import time
import urllib
import xml.etree.ElementTree as Et
from json import JSONDecodeError

import pandas as pd
import requests
from tqdm import tqdm

from .exceptions import IncorrectFieldException
from .exceptions import MissingQueryException
from .utils import requests_3_retries
from .utils import scientific_name_to_taxid

SEARCH_REQUEST_TIMEOUT = 20
SRA_SEARCH_GROUP_SIZE = 300


class QuerySearch:
    """This is the base class for the search feature.

    This class takes as input the user's search query, which has been
    tokenized by the ArgParser. The query will be sent to either SRA or ENA
    depending on the user's input, and the results will be returned as a
    pandas dataframe.

    Attributes
    ----------
    self.df: Pandas DataFrame
        The search result belonging to this search instance

    Parameters
    ----------
    verbosity : integer
        The level of details of the search result.
    return_max : int
        The maximum number of entries to be returned.
    query : str
        The main query string.
    accession : str
        A relevant study / experiment / sample / run accession number.
    organism  : str
        Scientific name of the sample organism
    layout : str
        Library layout. Possible inputs: single, paired
    mbases : int
        Size of the sample of interest rounded to the nearest megabase.
    publication_date : str
        The publication date of the run in the format dd-mm-yyyy. If a
        date range is desired, input should be in the format of
        dd-mm-yyyy:dd-mm-yyyy
    platform : str
        Sequencing platform used for the run. Some possible inputs include:
        illumina, ion torrent, oxford nanopore
    selection : str
        Library selection. Some possible inputs: cdna, chip, dnase, pcr
    source : str
        Library source. Some possible inputs: genomic, metagenomic,
        transcriptomic
    strategy : str
        Library Preparation strategy. Some possible inputs: wgs, amplicon,
        rna seq
    title : str
        Title of the experiment associated with the run
    suppress_validation: bool
        Defaults to False. If this is set to True, the user input format
        checks will be skipped.
        Setting this to True may cause the program to behave in unexpected
        ways, but allows the user to search queries that does not pass the
        format check.

    Methods
    -------
    get_df()
        Returns the dataframe storing this search result.

    search()
        Executes the search.

    show_result_statistics()
        Shows summary information about search results.

    visualise_results()
        Generate graphs that visualise the search results.

    get_plot_objects():
        Get the plot objects for plots generated.

    """

    def __init__(
        self,
        verbosity=2,
        return_max=20,
        query=None,
        accession=None,
        organism=None,
        layout=None,
        mbases=None,
        publication_date=None,
        platform=None,
        selection=None,
        source=None,
        strategy=None,
        title=None,
        suppress_validation=False,
    ):
        try:
            int_verbosity = int(verbosity)
            if int_verbosity not in range(4):
                raise ValueError
        except (TypeError, ValueError):
            raise IncorrectFieldException(
                f"Incorrect verbosity format: {verbosity}\n"
                "Verbosity must be an integer between 0 to 3 inclusive."
            )
        try:
            int_return_max = int(return_max)
            if int_return_max <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise IncorrectFieldException(
                f"Incorrect return_max format: {return_max}\n"
                "return_max must be a positive integer."
            )
        self.verbosity = int_verbosity
        self.return_max = int_return_max
        self.fields = {
            "query": query,
            "accession": accession,
            "organism": organism,
            "layout": layout,
            "mbases": mbases,
            "publication_date": publication_date,
            "platform": platform,
            "selection": selection,
            "source": source,
            "strategy": strategy,
            "title": title,
        }
        for k in self.fields:
            if type(self.fields[k]) == list:
                self.fields[k] = " ".join(self.fields[k])
        self.df = pd.DataFrame()
        # Verify that not all query fields are empty
        if not any(self.fields.values()):
            raise MissingQueryException()
        if not suppress_validation:
            self._validate_fields()
        self.stats = {
            "study": "-",
            "experiment": "-",
            "run": "-",
            "sample": "-",
            "Date range": "-",
            "Organisms": "-",
            "Library strategy": "-",
            "Library source": "-",
            "Library selection": "-",
            "Library layout": "-",
            "Platform": "-",
            "count_mean": "-",
            "count_median": "-",
            "count_stdev": "-",
        }
        self.plot_objects = {}

    def _input_multi_regex_checker(self, regex_matcher, input_query, error_message):
        """Checks if the user input match exactly 1 of the possible regex.

        This is a helper method for _validate_fields. It takes as input a
        dictionary of regex expression : accepted string by API pairs, and
        an input string, and verifies that the input string matches exactly
        one of the regex expressions.
        Matching multiple expressions indicates the input string is
        ambiguous, while matching none of the expressions suggests the
        input will likely produce no results or an error.
        Once matched, this method formats the user input so that it
        can be accepted by the API to be queried, as ENA especially expect
        case-sensitive exact matches for search queries.

        Parameters
        ----------
        regex_matcher : dict
            dictionary of regex expression : accepted string by API pairs.
        input_query : str
            input string for a particular query field.
        error_message : str
            error message to be shown if input_query does not match any of
            the regex expressions in regex_matcher.

        Returns
        -------
        tuple
            tuple pair of (input_query, message).
            message is "" if no format error has been identified, error
            message otherwise.
        """
        matched_strings = []
        for regex_expression in regex_matcher:
            if re.match(regex_expression, input_query, re.IGNORECASE):
                matched_strings.append(regex_matcher[regex_expression])
        if not matched_strings:
            return input_query, error_message
        elif len(matched_strings) == 1:
            return matched_strings[0], ""
        else:
            message = (
                f"Multiple potential matches have been identified for {input_query}:\n"
                f"{matched_strings}\n"
                f"Please check your input.\n\n"
            )
            return input_query, message

    def _validate_fields(self):
        """Verifies that user input format is correct.

        This helper function tries to match the input query strings from
        the user to the exact string that is accepted by both SRA and ENA

        Note: as of the implementation of this method, ENA does not have
        a documentation page listing the accepted values for query
        parameters. The list of parameters below were collected from ENA's
        advanced search page: https://www.ebi.ac.uk/ena/browser/advanced-search

        Updating new values:
        If any new values are accepted by ENA, it should appear under
        the corresponding parameter in the page. To update this method,
        think of a regex that captures what the user may type for the new
        value, and include it in the respective xxx_matcher dictionary
        below as a regex:value key value pair.

        Eg: if a new sequencing platform, Pokemon, is added to ENA,
        navigate to "Instrument Platform" parameter on ENA's advanced
        search page and copy the corresponding phrase (eg "poKe_Mon").
        Then add the key value pair ".*poke.*": "poKe_Mon" to
        platform_matcher below.

        Unlike SRA, ENA requires supplied param values to be exact match
        to filter accordingly (eg "cDNA_oligo_dT"), which motivated this
        feature.

        Raises
        ------
        IncorrectFieldException
            If the input to any query field is in the wrong format

        """

        message = ""

        # verify layout
        if self.fields["layout"] and str(self.fields["layout"]).upper() not in [
            "SINGLE",
            "PAIRED",
        ]:
            message += (
                f"Incorrect layout field format: {self.fields['layout']}\n"
                "--layout must be either SINGLE or PAIRED\n\n"
            )
        # verify mbases
        if self.fields["mbases"]:
            try:
                self.fields["mbases"] = int(self.fields["mbases"])
                if self.fields["mbases"] <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                message += (
                    f"Incorrect mbases format: {self.fields['mbases']}\n"
                    f"--mbases must be a positive integer\n\n"
                )
        # verify publication_date
        date_regex = "(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(19|20)[0-9]{2}"
        if self.fields["publication_date"] and not re.match(
            f"^{date_regex}(:{date_regex})?$", self.fields["publication_date"]
        ):
            message += (
                f"Incorrect publication date format: {self.fields['publication_date']}\n"
                f"Expected --publication-date format: dd-mm-yyyy or dd-mm-yyyy:dd-mm-yyyy, between 1900-2099\n\n"
            )
        # verify platform
        platform_matcher = {
            ".*oxford.*|.*nanopore.*": "OXFORD_NANOPORE",
            ".*illumina.*": "ILLUMINA",
            ".*ion.*torrent.*": "ION_TORRENT",
            ".*capillary.*": "CAPILLARY",
            ".*pacbio.*|.*smrt.*": "PACBIO_SMRT",
            ".*abi.*solid.*": "ABI_SOLID",
            ".*bgi.*": "BGISEQ",
            ".*454.*": "LS454",
            ".*complete.*genomics.*": "COMPLETE_GENOMICS",
            ".*helicos.*": "HELICOS",
        }
        if self.fields["platform"]:
            error_message = (
                f"Incorrect platform: {self.fields['platform']}\n"
                f"--platform must be one of the following: \n"
                f"OXFORD_NANOPORE, ILLUMINA, ION_TORRENT, \n"
                f"CAPILLARY, PACBIO_SMRT, ABI_SOLID, \n"
                f"BGISEQ, LS454, COMPLETE_GENOMICS, HELICOS\n\n"
            )
            output = self._input_multi_regex_checker(
                platform_matcher, self.fields["platform"], error_message
            )
            if output[1]:
                message += output[1]
            else:
                self.fields["platform"] = output[0]
        # verify selection
        selection_matcher = {
            ".*methylcytidine.*": "5-methylcytidine antibody",
            ".*cage.*": "CAGE",
            r".*chip\s*$": "ChIP",
            ".*chip.*seq.*": "ChIP-Seq",
            ".*dnase.*": "DNase",
            ".*hmpr.*": "HMPR",
            ".*hybrid.*": "Hybrid Selection",
            r".*inverse.*rrna\s*$": "Inverse rRNA",
            ".*inverse.*rrna.*selection.*": "Inverse rRNA selection",
            ".*mbd2.*protein.*methyl.*cpg.*binding.*domain.*": "MBD2 protein methyl-CpG binding domain",
            ".*mda.*": "MDA",
            ".*mf.*": "MF",
            ".*mnase.*": "MNase",
            ".*msll.*": "MSLL",
            r"^\s*oligo.*dt.*": "Oligo-dT",
            r"^\s*pcr\s*$": "PCR",
            ".*poly[ -_]*a.*": "PolyA",
            ".*race.*": "RACE",
            r".*random\s*$": "RANDOM",
            ".*random.*pcr.*": "RANDOM PCR",
            ".*rt[ -_]*pcr.*": "RT-PCR",
            ".*reduced.*representation.*": "Reduced Representation",
            ".*restriction.*digest.*": "Restriction Digest",
            r".*cdna\s*$": "cDNA",
            ".*cdna.*oligo.*dt": "cDNA_oligo_dT.*",  # ENA only
            ".*cdna.*random.*priming": "cDNA_randomPriming.*",  # ENA only
            ".*other.*": "other",
            ".*padlock.*probes.*capture.*method.*": "padlock probes capture method",
            ".*repeat.*fractionation.*": "repeat fractionation",
            ".*size.*fractionation.*": "size fractionation",
            ".*unspecified.*": "unspecified",
        }
        if self.fields["selection"]:
            error_message = (
                f"Incorrect selection: {self.fields['selection']}\n"
                f"--selection must be one of the following: \n"
                f"5-methylcytidine antibody, CAGE, ChIP, ChIP-Seq, DNase, HMPR, Hybrid Selection,  \n"
                f"Inverse rRNA, Inverse rRNA selection, MBD2 protein methyl-CpG binding domain, \n"
                f"MDA, MF, MNase, MSLL, Oligo-dT, PCR, PolyA, RACE, RANDOM, RANDOM PCR, RT-PCR,  \n"
                f"Reduced Representation, Restriction Digest, cDNA, cDNA_oligo_dT, cDNA_randomPriming \n"
                f"other, padlock probes capture method, repeat fractionation, size fractionation, \n"
                f"unspecified\n\n"
            )
            output = self._input_multi_regex_checker(
                selection_matcher, self.fields["selection"], error_message
            )
            if output[1]:
                message += output[1]
            else:
                self.fields["selection"] = output[0]
        # verify source
        source_matcher = {
            r"^\s*genomic\s*$": "GENOMIC",
            ".*genomic.*single.*cell.*": "GENOMIC SINGLE CELL",
            ".*metagenomic.*": "METAGENOMIC",
            ".*metatranscriptomic.*": "METATRANSCRIPTOMIC",
            ".*other.*": "OTHER",
            ".*synthetic.*": "SYNTHETIC",
            r"^\s*transcriptomic\s*$": "TRANSCRIPTOMIC",
            ".*transcriptomic.*single.*cell.*": "TRANSCRIPTOMIC SINGLE CELL",
            ".*viral.*rna.*": "VIRAL RNA",
        }
        if self.fields["source"]:
            error_message = (
                f"Incorrect source: {self.fields['source']}\n"
                f"--source must be one of the following: \n"
                f"GENOMIC, GENOMIC SINGLE CELL, METAGENOMIC,  \n"
                f"METATRANSCRIPTOMIC, OTHER, SYNTHETIC, \n"
                f"TRANSCRIPTOMIC, TRANSCRIPTOMIC SINGLE CELL, VIRAL RNA\n\n"
            )
            output = self._input_multi_regex_checker(
                source_matcher, self.fields["source"], error_message
            )
            if output[1]:
                message += output[1]
            else:
                self.fields["source"] = output[0]
        # verify strategy
        strategy_matcher = {
            ".*amplicon.*": "AMPLICON",
            ".*atac.*": "ATAC-seq",
            ".*bisulfite.*": "Bisulfite-Seq",
            r"^\s*clone\s*$": "CLONE",
            ".*cloneend.*": "CLONEEND",
            ".*cts.*": "CTS",
            ".*chia.*|.*pet.*": "ChIA-PET",
            ".*chip.*seq.*": "ChIP-Seq",
            ".*dnase.*|.*hypersensitivity.*": "DNase-Hypersensitivity",
            r"^\s*est\s*$": "EST",
            ".*faire.*": "FAIRE-seq",
            ".*finishing.*": "FINISHING",
            ".*fl.*cdna.*": "FL-cDNA",
            ".*hi.*c.*": "Hi-C",
            ".*mbd.*": "MBD-Seq",
            ".*mnase.*": "MNase-Seq",
            ".*mre.*": "MRE-Seq",
            ".*medip.*": "MeDIP-Seq",
            ".*other.*": "OTHER",
            ".*poolclone.*": "POOLCLONE",
            ".*rad.*": "RAD-Seq",
            ".*rip.*": "RIP-Seq",
            r"^\s*rna.*seq": "RNA-Seq",
            ".*selex.*": "SELEX",
            ".*synthetic.*|.*long.*read.*": "Synthetic-Long-Read",
            ".*targeted.*capture.*": "Targeted-Capture",
            ".*tethered.*chromatin.*conformation.*capture.*|.*tccc.*": "Tethered Chromatin Conformation Capture",
            ".*tn.*": "Tn-Seq",
            ".*validation.*": "VALIDATION",
            ".*wcs.*": "WCS",
            ".*wga.*": "WGA",
            ".*wgs.*": "WGS",
            ".*wxs.*": "WXS",
            ".*mirna.*": "miRNA-Seq",
            ".*ncrna.*": "ncRNA-Seq",
            ".*ssrna.*": "ssRNA-seq",
            ".*gbs.*": "GBS",
        }
        if self.fields["strategy"]:
            error_message = (
                f"Incorrect strategy: {self.fields['strategy']}\n"
                f"--strategy must be one of the following: \n"
                f"AMPLICON, ATAC-seq, Bisulfite-Seq, CLONE, CLONEEND, CTS, ChIA-PET, ChIP-Seq, \n"
                f"DNase-Hypersensitivity, EST, FAIRE-seq, FINISHING, FL-cDNA, Hi-C, MBD-Seq, MNase-Seq,\n"
                f"MRE-Seq, MeDIP-Seq, OTHER, POOLCLONE, RAD-Seq, RIP-Seq, RNA-Seq, SELEX, \n"
                f"Synthetic-Long-Read, Targeted-Capture, Tethered Chromatin Conformation Capture, \n"
                f"Tn-Seq, VALIDATION, WCS, WGA, WGS, WXS, miRNA-Seq, ncRNA-Seq, ssRNA-seq, GBS\n\n"
            )
            output = self._input_multi_regex_checker(
                strategy_matcher, self.fields["strategy"], error_message
            )
            if output[1]:
                message += output[1]
            else:
                self.fields["strategy"] = output[0]
        if message:
            raise IncorrectFieldException(message)

    def _list_stat(self, stat_header):
        stat = self.stats[stat_header]
        if type(stat) != dict:
            return f"  {stat_header}: {stat}\n"
        keys = sorted(stat.keys())
        stat_breakdown = "\n"
        for key in keys:
            stat_breakdown += f"\t  {key}:  {stat[key]}\n"
        return f"  {stat_header}: {stat_breakdown}\n"

    def show_result_statistics(self):
        """Shows search result statistics."""
        if self.df.empty:
            print(
                "No results are found for the current search query, hence no statistics can be generated."
            )
            return
        stats = (
            "\n  Statistics for the search query:\n"
            + "  =================================\n"
            + f"  Number of unique studies: {self.stats['study']}\n"
            + f"  Number of unique experiments: {self.stats['experiment']}\n"
            + f"  Number of unique runs: {self.stats['run']}\n"
            + f"  Number of unique samples: {self.stats['sample']}\n"
            + f"  Mean base count of samples: {self.stats['count_mean']:.3f}\n"
            + f"  Median base count of samples: {self.stats['count_median']:.3f}\n"
            + f"  Sample base count standard deviation: {self.stats['count_stdev']:.3f}\n"
        )

        # Statistics with categorical breakdowns:
        categorical_stats = (
            "Date range",
            "Organisms",
            "Platform",
            "Library strategy",
            "Library source",
            "Library selection",
            "Library layout",
        )
        for categorical_stat in categorical_stats:
            stats += self._list_stat(categorical_stat)
        print(stats)

    def visualise_results(
        self, graph_types=("all",), show=False, saveto="./search_plots/"
    ):
        """Generate graphs that visualise the search results.

        This method will only work if the optional dependency, matplotlib,
        is installed in the system.

        Parameters
        ----------
        graph_types : tuple
            tuple containing strings representing types of graphs to
            generate.
            Possible strings: all, daterange, organism, source, selection, platform,
            basecount
        saveto : str
            directory name where the generated graphs are saved.

        show : bool
            Whether plotted graphs are immediately shown.
        """
        if self.df.empty:
            print(
                "No results are found for the current search query, hence no graphs can be generated."
            )
            return
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print(
                "The optional dependency, matplotlib, is not available on the system.\n"
                "matplotlib is required to generate graphs to visualise search results.\n"
                'You can install matplotlib by typing "pip install matplotlib" on the command line.\n'
            )
            return
        plt.rcParams["figure.autolayout"] = True
        if not os.path.isdir(saveto):
            os.mkdir(saveto)
        plots = [
            ("Base Count",),
            ("Publication Date",),
            ("Organism",),
            ("Library Source",),
            ("Library Selection",),
            ("Platform",),
            ("Organism", "Publication Date"),
            ("Library Source", "Publication Date"),
            ("Library Selection", "Publication Date"),
            ("Platform", "Publication Date"),
            ("Library Source", "Organism"),
            ("Library Selection", "Organism"),
            ("Platform", "Organism"),
            ("Library Selection", "Library Source"),
            ("Platform", "Library Source"),
            ("Platform", "Library Selection"),
        ]
        plot_keys = {
            "daterange": "Publication Date",
            "organism": "Organism",
            "source": "Library Source",
            "selection": "Library Selection",
            "platform": "Platform",
            "basecount": "Base Count",
        }
        if "all" not in graph_types:
            selected_plots = []
            for graph_type in graph_types:
                if graph_type not in plot_keys:
                    continue
                for plot in plots:
                    if plot_keys[graph_type] in plot and plot not in selected_plots:
                        selected_plots.append(plot)
            plots = selected_plots
        too_many_organisms = False
        if self.stats["graph_raw"]["Organism"].nunique() > 30:
            print(
                "Too many types of organisms to plot (>30). Showing only top 30 organisms."
            )
            too_many_organisms = True
        for plot in plots:
            self._plot_graph(plt, plot, show, saveto, too_many_organisms)

    def search(self):
        pass

    def get_df(self):
        """Getter for the search result dataframe."""
        return self.df

    def get_plot_objects(self):
        """Get the plot objects for plots generated."""
        return self.plot_objects

    def _plot_graph(self, plt, axes, show, savedir, too_many_organisms):
        """Plots a graph based on data from self.stats

        Parameters
        ----------
        axes: tuple
            tuple containing 1 or 2 strings corresponding to the statistics
            to plot. 1 string: Histogram. 2 string: heat map
        savedir: str
            directory to save to
        show: bool
            whether to call plt.show
        """
        timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
        if (
            "Publication Date" in axes
            and self.stats["graph_raw"]["Publication Date"].nunique() > 30
        ):
            self.stats["graph_raw"]["Publication Date"] = self.stats["graph_raw"][
                "Publication Date"
            ].str[:-3]
        if axes == ("Base Count",):
            count = list(self.stats["count_data"])
            if len(count) == 0:
                return
            title = "Histogram of Base Count"
            plt.figure(figsize=(15, 10))
            plt.hist(count, min(70, len(count)), color="#135c1c", log=True)
            plt.xlabel("Base Count", fontsize=14)
            plt.ylabel("Frequency", fontsize=14)
            plt.xticks(rotation=90)
            plt.title(title, fontsize=18)
            plt.savefig(f"{savedir}{title} {timestamp}.svg")
            self.plot_objects[axes] = plt
        elif len(axes) == 1:
            title = f"Histogram of {axes[0]}"
            data = self.stats["graph_raw"][axes[0]].value_counts()
            if too_many_organisms:
                data = data[:30]
            plt.figure(figsize=(15, 10))
            plt.bar(
                range(len(data.values)),
                data.values,
                tick_label=list(data.index),
                color="#135c1c",
            )
            plt.xticks(rotation=90)
            plt.title(title, fontsize=18)
            plt.xlabel(axes[0], fontsize=14)
            plt.ylabel("Frequency", fontsize=14)
            plt.savefig(f"{savedir}{title} {timestamp}.svg")
            self.plot_objects[axes] = plt
        elif len(axes) == 2:
            title = f"Heatmap of {axes[0]} against {axes[1]}"
            df = self.stats["graph_raw"][list(axes)]
            a = df.groupby([axes[0]]).agg({i: "value_counts" for i in df.columns[1:]})
            a = a.rename(columns={axes[1]: f"{axes[1]}_count"})
            b = a.reset_index(level=list(axes))
            piv = (
                pd.pivot_table(
                    b,
                    values=f"{axes[1]}_count",
                    index=[axes[0]],
                    columns=[axes[1]],
                    fill_value=0,
                    aggfunc="sum",
                    margins=True,
                )
                .sort_values("All", ascending=False)
                .drop("All", axis=1)
                .sort_values("All", ascending=False, axis=1)
                .drop("All")
            )
            if too_many_organisms:
                if axes[0] == "Organism":
                    piv = piv[:30]
                else:
                    piv = piv.iloc[:, :30]
            fig, ax = plt.subplots(figsize=(15, 12))
            im = ax.imshow(piv, cmap="Greens")
            fig.colorbar(im, ax=ax)
            ax.set_title(title, fontsize=18)
            ax.set_xticks(range(len(piv.columns)))
            ax.set_yticks(range(len(piv.index)))
            ax.set_xticklabels(piv.columns, rotation=90)
            ax.set_yticklabels(piv.index)
            ax.set_ylabel(axes[0], fontsize=14)
            ax.set_xlabel(axes[1], fontsize=14)
            ax.get_figure().savefig(f"{savedir}{title} {timestamp}.svg")
            self.plot_objects[axes] = (fig, ax)
        if show:
            plt.show()


class SraSearch(QuerySearch):
    """Subclass of QuerySearch that implements search by querying
    NCBI Entrez API

    Methods
    -------
    search()
        sends the user query via requests to NCBI Entrez API and returns
        search results as a pandas dataframe.

    show_result_statistics()
        Shows summary information about search results.

    visualise_results()
        Generate graphs that visualise the search results.

    get_plot_objects():
        Get the plot objects for plots generated.

    get_uids():
        Get NCBI uids retrieved during this search query.

    _format_query_string()
        formats the input user query into a string

    _format_request()
        formats the request payload

    _format_result(content)
        formats the search query output.

    See Also
    --------
    QuerySearch: Superclass of SraSearch

    """

    def __init__(
        self,
        verbosity=2,
        return_max=20,
        query=None,
        accession=None,
        organism=None,
        layout=None,
        mbases=None,
        publication_date=None,
        platform=None,
        selection=None,
        source=None,
        strategy=None,
        title=None,
        suppress_validation=False,
    ):
        super().__init__(
            verbosity,
            return_max,
            query,
            accession,
            organism,
            layout,
            mbases,
            publication_date,
            platform,
            selection,
            source,
            strategy,
            title,
            suppress_validation,
        )
        self.entries = {}
        self.number_entries = 0
        self.uids = []

    def search(self):
        # Step 1: retrieves the list of uids that satisfies the input
        # search query
        payload = self._format_request()
        try:
            r = requests_3_retries().get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params=payload,
                timeout=SEARCH_REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            self.uids = r.json()["esearchresult"]["idlist"]

            # Step 2: retrieves the detailed information for each uid
            # returned, in groups of SRA_SEARCH_GROUP_SIZE.
            if not self.uids:
                print(
                    f"No results found for the following search query: \n {self.fields}"
                )
                return  # If no queries found, return nothing
            pbar = tqdm(total=len(self.uids))
            for i in range(0, len(self.uids), SRA_SEARCH_GROUP_SIZE):
                current_uids = ",".join(
                    self.uids[i : min(i + SRA_SEARCH_GROUP_SIZE, len(self.uids))]
                )
                pbar.update(min(SRA_SEARCH_GROUP_SIZE, len(self.uids) - i))
                payload2 = {"db": "sra", "retmode": "xml", "id": current_uids}

                r = requests_3_retries().get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                    params=payload2,
                    timeout=SEARCH_REQUEST_TIMEOUT,
                    stream=True,
                )
                r.raise_for_status()
                r.raw.decode_content = True
                self._format_response(r.raw)
            pbar.close()
            self._format_result()

        except requests.exceptions.Timeout:
            sys.exit(f"Connection to the server has timed out. Please retry.")
        except requests.exceptions.HTTPError:
            sys.exit(
                f"HTTPError: This is likely caused by an invalid search query: "
                f"\nURL queried: {r.url} \nUser query: {self.fields}"
            )

    def get_uids(self):
        """Get NCBI uids retrieved during this search query.

        Note: There is a chance that some uids retrieved do not appear in
        the search result output (Refer to #88)
        """
        return self.uids

    def _format_query_string(self):
        term = ""
        if self.fields["query"]:
            term += self.fields["query"] + " AND "
        if self.fields["accession"]:
            term += self.fields["accession"] + "[Accession] AND "
        if self.fields["organism"]:
            term += self.fields["organism"] + "[Organism] AND "
        if self.fields["layout"]:
            term += self.fields["layout"] + "[Layout] AND "
        if self.fields["mbases"]:
            term += str(self.fields["mbases"]) + "[Mbases] AND "
        if self.fields["publication_date"]:
            dates = []
            for date in self.fields["publication_date"].split(":"):
                dates.append("/".join(date.split("-")[::-1]))
            term += ":".join(dates) + "[PDAT] AND "
        if self.fields["platform"]:
            term += self.fields["platform"] + "[Platform] AND "
        if self.fields["selection"]:
            term += self.fields["selection"] + "[Selection] AND "
        if self.fields["source"]:
            term += self.fields["source"] + "[Source] AND "
        if self.fields["strategy"]:
            term += self.fields["strategy"] + "[Strategy] AND "
        if self.fields["title"]:
            term += self.fields["title"] + "[Title] AND "
        return term[:-5]  # Removing trailing " AND "

    def _format_request(self):
        payload = {
            "db": "sra",
            "term": self._format_query_string(),
            "retmode": "json",
            "retmax": self.return_max,
        }
        return payload

    def _format_response(self, content):
        field_categories = [
            "EXPERIMENT",
            "SUBMISSION",
            "ORGANISATION",
            "STUDY",
            "SAMPLE",
            "Pool",
            "RUN_SET",
        ]
        for event, elem in Et.iterparse(content):
            if elem.tag == "EXPERIMENT_PACKAGE":
                self.number_entries += 1
            elif elem.tag in field_categories:
                self._parse_entry(elem)
        for field in self.entries:
            if len(self.entries[field]) < self.number_entries:
                self.entries[field] += [""] * (
                    self.number_entries - len(self.entries[field])
                )

    def _format_result(self):
        self.df = pd.DataFrame.from_dict(self.entries).replace(
            r"^\s*$", pd.NA, regex=True
        )
        self.entries.clear()
        if self.df.empty:
            return
        # Tabulate statistics
        self._update_stats()

        columns = list(self.df.columns)
        important_columns = [
            "study_accession",
            "experiment_accession",
            "experiment_title",
            "design_description",
            "sample_taxon_id",
            "sample_scientific_name",
            "experiment_library_strategy",
            "experiment_library_source",
            "experiment_library_selection",
            "sample_accession",
            "sample_alias",
            "experiment_instrument_model",
            "pool_member_spots",
            "run_1_size",
            "run_1_accession",
            "run_1_total_spots",
            "run_1_total_bases",
        ]
        temp_cols = []
        for col in important_columns:
            if col in columns:
                temp_cols.append(col)
                columns.remove(col)
        important_columns = temp_cols
        if self.verbosity <= 1:
            temp_dfs = []
            for col in self.df.columns:
                if re.match("run_[0-9]+_accession", col):
                    temp_df = self.df[[col, "experiment_title"]]
                    temp_df = temp_df[~pd.isna(temp_df[col])].rename(
                        columns={
                            col: "run_accession",
                            "experiment_title": "experiment_title",
                        }
                    )
                    temp_dfs.append(temp_df)
            run_dataframe = pd.concat(temp_dfs)
            run_dataframe.sort_values(by=["run_accession"], kind="mergesort")
            self.df = run_dataframe
        if self.verbosity == 0:
            self.df = self.df[["run_accession"]]
        elif self.verbosity == 1:
            pass  # df has already been formatted above
        elif self.verbosity == 2:
            self.df = self.df[important_columns]
        elif self.verbosity == 3:
            self.df = self.df[important_columns + sorted(columns)]
        self.df.dropna(how="all")

    def _parse_entry(self, entry_root):
        """Parses a subset of the XML tree from request stream

        Parameters
        ----------
        entry_root: ElementTree.Element
            root element of the xml tree from requests stream
        """
        field_header = entry_root.tag.lower()
        run_count = 0

        # root element attributes
        for k, v in entry_root.attrib.items():
            self._update_entry(f"{field_header}_{k}".lower(), v)
        for child in entry_root:
            # "*_REF" tags contain duplicate information that can be found
            # somewhere in the xml entry and are skipped
            if child.tag.endswith("_REF"):
                continue
            # IDENTIFIERS contain two types of children tags:
            # PRIMARY_ID, which repeats the accession number and
            # EXTERNAL_ID tags, each containing an alternative ID that is
            # typically used in another database (GEO, ENA etc)
            # IDs are numbered from 1 to differentiate between them.
            elif child.tag == "IDENTIFIERS":
                id_index = 1
                for identifier in child:
                    if identifier.tag == "EXTERNAL_ID":
                        self._update_entry(
                            f"{field_header}_external_id_{id_index}",
                            identifier.text,
                        )
                        self._update_entry(
                            f"{field_header}_external_id_{id_index}_namespace",
                            identifier.get("namespace"),
                        )
            # "*_LINKS" tags contain 0 or more "*_LINK" children tags,
            # each containing information (values) regarding the link
            # Links are numbered from 1 to differentiate between multiple
            # links.
            elif child.tag.endswith("_LINKS"):
                link_index = 1
                for link in child:
                    # Link type. Eg: URL_link, Xref_link
                    self._update_entry(
                        f"{link.tag}_{link_index}_type".lower(),
                        link[0].tag,
                    )
                    # Link values in the form of tag: value.
                    # Eg: label: GEO sample
                    link_value_index = 1
                    for link_value in link[0]:
                        self._update_entry(
                            f"{link.tag}_{link_index}_value_{link_value_index}".lower(),
                            f"{link_value.tag}: {link_value.text}",
                        )
                        link_value_index += 1
                    link_index += 1
            # "*_ATTRIBUTES" tags contain tag - value pairs providing
            # additional information for the Experiment/Sample/Study
            # Attributes are numbered from 1 to differentiate between
            # multiple attributes.
            elif child.tag.endswith("_ATTRIBUTES"):
                attribute_index = 1
                for attribute in child:
                    for val in attribute:
                        self._update_entry(
                            f"{child.tag}_{attribute_index}_{val.tag}".lower(),
                            val.text,
                        )
                    attribute_index += 1
            # Differentiating between sample title and experiment title.
            elif child.tag == "TITLE":
                self._update_entry(f"{field_header}_title", child.text)
            # Parsing platfrom information
            elif child.tag == "PLATFORM":
                platform = child[0]
                self._update_entry("experiment_platform", platform.tag)
                self._update_entry(
                    "experiment_instrument_model",
                    platform[0].text,
                )
            # Parsing individual run information
            elif child.tag == "RUN":
                run_count += 1
                # run attributes
                for k, v in child.attrib.items():
                    self._update_entry(f"run_{run_count}_{k}".lower(), v)
                for elem in child:
                    if elem.tag == "SRAFiles":
                        srafile_index = 1
                        for srafile in elem:
                            for k, v in srafile.attrib.items():
                                self._update_entry(
                                    f"run_{run_count}_srafile_{srafile_index}_{k}".lower(),
                                    v,
                                )
                            alternatives_index = 1
                            for alternatives in srafile:
                                for k, v in alternatives.attrib.items():
                                    self._update_entry(
                                        f"run_{run_count}_srafile_{srafile_index}_alternative_{alternatives_index}_{k}".lower(),
                                        v,
                                    )
                                alternatives_index += 1
                            srafile_index += 1
                    elif elem.tag == "CloudFiles":
                        cloudfile_index = 1
                        for cloudfile in elem:
                            for k, v in cloudfile.attrib.items():
                                self._update_entry(
                                    f"run_{run_count}_cloudfile_{cloudfile_index}_{k}".lower(),
                                    v,
                                )
                            cloudfile_index += 1
                    elif elem.tag == "Bases":
                        for k, v in elem.attrib.items():
                            self._update_entry(
                                f"run_{run_count}_total_base_{k}".lower(),
                                v,
                            )
                        for base in elem:
                            self._update_entry(
                                f"run_{run_count}_base_{base.attrib['value']}_count",
                                base.attrib["count"],
                            )
                    elif elem.tag == "Databases":
                        database_index = 1
                        for database in elem:
                            self._update_entry(
                                f"run_{run_count}_database_{database_index}".lower(),
                                Et.tostring(database).decode(),
                            )
                            database_index += 1
            else:
                for elem in child.iter():
                    # Tags to ignore to avoid confusion
                    if elem.tag in ["PRIMARY_ID", "SINGLE", "PAIRED"]:
                        continue
                    elif elem.text:
                        self._update_entry(
                            f"{field_header}_{elem.tag.lower()}",
                            elem.text,
                        )
                    elif elem.attrib:
                        for k, v in elem.attrib.items():
                            self._update_entry(
                                f"{field_header}_{elem.tag}_{k}".lower(),
                                v,
                            )
            # Parsing library layout (single, paired)
            if field_header == "experiment":
                library_layout = child.find("./LIBRARY_DESCRIPTOR/LIBRARY_LAYOUT")
                if library_layout:
                    library_layout = library_layout[0]
                    self._update_entry(f"library_layout", library_layout.tag)
                    # If library layout is paired, information such as nominal
                    # standard deviation and length, etc are provided as well.
                    if library_layout.tag == "PAIRED":
                        for k, v in library_layout.attrib.items():
                            self._update_entry(
                                f"library_layout_{k}".lower(),
                                v,
                            )

    def _update_entry(self, field_name, field_content):
        """Adds information from a field into the entries dictionary

        This is a helper function that adds information parsed from the XML
        output from SRA into a dictionary of lists, for easier conversion
        into a Pandas dataframe later. Dictionary key is created if it
        doesn't exist yet. For entries that does not have information
        belonging to a field, the corresponding list will be padded with
        empty strings.

        Parameters
        ----------
        field_name: str
            Name of the field where a value belonging to an entry is to be
            added
        field_content: str
            Value to be added
        """
        if field_name not in self.entries:
            self.entries[field_name] = []
        if len(self.entries[field_name]) > self.number_entries:
            return
        self.entries[field_name] += [""] * (
            self.number_entries - len(self.entries[field_name])
        ) + [field_content]

    def _update_stats(self):
        # study
        self.stats["study"] = self.df["study_accession"].nunique()
        # experiment
        self.stats["experiment"] = self.df["experiment_accession"].nunique()
        # run
        runs = self._merge_selected_columns(r"^run.*accession$")
        if not runs.empty:
            self.stats["run"] = runs.nunique()
        # sample
        samples = self._merge_selected_columns(r"^sample.*accession$")
        if not samples.empty:
            self.stats["sample"] = samples.nunique()
        # date range
        daterange = self._merge_selected_columns(r"^run_1_published$")
        if not daterange.empty:
            dates = pd.to_datetime(daterange).dt.to_period("M").astype(str)
            self.stats["Date range"] = dates.value_counts().to_dict()
        # organisms
        organisms = self._merge_selected_columns(r"^sample.*scientific_name.*")
        if not organisms.empty:
            self.stats["Organisms"] = organisms.value_counts().to_dict()
        # strategy
        if "experiment_library_strategy" in self.df.columns:
            self.stats["Library strategy"] = (
                self.df["experiment_library_strategy"].value_counts().to_dict()
            )
        # source
        if "experiment_library_source" in self.df.columns:
            self.stats["Library source"] = (
                self.df["experiment_library_source"].value_counts().to_dict()
            )
        # selection
        if "experiment_library_selection" in self.df.columns:
            self.stats["Library selection"] = (
                self.df["experiment_library_selection"].value_counts().to_dict()
            )
        # layout
        if "library_layout" in self.df.columns:
            self.stats["Library layout"] = (
                self.df["library_layout"].value_counts().to_dict()
            )
        # platform
        if "experiment_platform" in self.df.columns:
            self.stats["Platform"] = (
                self.df["experiment_platform"].value_counts().to_dict()
            )
        # count
        count = self._merge_selected_columns(r"^run_.*_total_bases$").astype("int64")
        self.stats["count_data"] = count
        self.stats["count_mean"] = count.mean()
        self.stats["count_median"] = count.median()
        self.stats["count_stdev"] = count.std()

        # for graphing
        self.stats["graph_raw"] = self.df[
            [
                "sample_scientific_name",
                "experiment_library_strategy",
                "experiment_library_source",
                "experiment_library_selection",
                "run_1_published",
                "experiment_platform",
            ]
        ].rename(
            columns={
                "sample_scientific_name": "Organism",
                "experiment_library_strategy": "Library Strategy",
                "experiment_library_source": "Library Source",
                "experiment_library_selection": "Library Selection",
                "run_1_published": "Publication Date",
                "experiment_platform": "Platform",
            }
        )
        self.stats["graph_raw"]["Publication Date"] = (
            pd.to_datetime(
                self.stats["graph_raw"]["Publication Date"].replace(pd.NA, None)
            )
            .dt.to_period("M")
            .astype(str)
        )

    def _merge_selected_columns(self, regex):
        columns = list(self.df.filter(regex=regex, axis=1).columns)
        if not columns:
            series = pd.Series(dtype="object")
        elif len(columns) == 1:
            series = self.df[columns[0]]
        else:
            series = self.df[columns[0]].append(
                [self.df[c] for c in columns[1:]], ignore_index=True
            )
        return series[~pd.isna(series)]


class EnaSearch(QuerySearch):
    """Subclass of QuerySearch that implements search via querying ENA API


    Methods
    -------
    search()
        sends the user query via requests to ENA API and stores search
        result as an instance attribute in the form of a pandas dataframe

    show_result_statistics()
        Shows summary information about search results.

    visualise_results()
        Generate graphs that visualise the search results.

    get_plot_objects():
        Get the plot objects for plots generated.

    _format_query_string()
        formats the input user query into a string

    _format_request()
        formats the request payload

    _format_result(content)
        formats the search query output and converts it into a pandas
        dataframe

    See Also
    --------
    QuerySearch: Superclass of EnaSearch

    """

    def search(self):
        # This ensures that the spaces in the query string are not
        # converted to '+' by requests.
        payload = urllib.parse.urlencode(
            self._format_request(), quote_via=urllib.parse.quote
        )
        try:
            r = requests_3_retries().get(
                "https://www.ebi.ac.uk/ena/portal/api/search",
                params=payload,
                timeout=SEARCH_REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            self._format_result(r.json())
        except requests.exceptions.Timeout:
            sys.exit(f"Connection to the server has timed out. Please retry.")
        except requests.exceptions.HTTPError:
            sys.exit(
                f"HTTPError: This is likely caused by an invalid search query: "
                f"\nURL queried: {r.url} \nUser query: {self.fields}"
            )
        except JSONDecodeError:
            print(f"No results found for the following search query: \n {self.fields}")
            return  # no results found

    def _format_query_string(self):
        term = ""
        if self.fields["query"]:
            term += rf'(experiment_title="*{self.fields["query"]}*"'
            if not self.fields["accession"]:
                self.fields["query"] = self.fields["query"].upper()
                term += (
                    rf' OR study_accession="{self.fields["query"]}" OR '
                    rf'secondary_study_accession="{self.fields["query"]}" OR '
                    rf'sample_accession="{self.fields["query"]}" OR '
                    rf'secondary_sample_accession="{self.fields["query"]}" OR '
                    rf'experiment_accession="{self.fields["query"]}" OR '
                    rf'submission_accession="{self.fields["query"]}" OR '
                    rf'run_accession="{self.fields["query"]}"'
                )
            term += ") AND "
        if self.fields["accession"]:
            self.fields["accession"] = self.fields["accession"].upper()
            term += (
                rf'(study_accession="{self.fields["accession"]}" OR '
                rf'secondary_study_accession="{self.fields["accession"]}" OR '
                rf'sample_accession="{self.fields["accession"]}" OR '
                rf'secondary_sample_accession="{self.fields["accession"]}" OR '
                rf'experiment_accession="{self.fields["accession"]}" OR '
                rf'submission_accession="{self.fields["accession"]}" OR '
                rf'run_accession="{self.fields["accession"]}") AND '
            )
        if self.fields["organism"]:
            term += rf'tax_eq({scientific_name_to_taxid(self.fields["organism"])}) AND '
        if self.fields["layout"]:
            term += rf'library_layout="{self.fields["layout"].upper()}" AND '
        if self.fields["mbases"]:
            if type(self.fields["mbases"]) != int:
                raise IncorrectFieldException(
                    f"Incorrect mbases format: {self.fields['mbases']}\n"
                    f"--mbases must be an integer"
                )
            upper_limit = self.fields["mbases"] * 1000000 + 500000
            lower_limit = self.fields["mbases"] * 1000000 - 500000
            term += rf"base_count>={lower_limit} AND base_count<{upper_limit} AND "
        if self.fields["publication_date"]:
            dates = self.fields["publication_date"].split(":")
            for i in range(len(dates)):
                dates[i] = "-".join(dates[i].split("-")[::-1])
            if len(dates) == 1:
                term += rf"first_created={dates[0]} AND "
            elif len(dates) == 2:
                term += rf"first_created>={dates[0]} AND first_created<={dates[1]} AND "
            else:
                raise IncorrectFieldException(
                    f"Incorrect publication date format: {self.fields['publication_date']}\n"
                    f"Expected format: dd-mm-yyyy or dd-mm-yyyy:dd-mm-yyyy"
                )
        if self.fields["platform"]:
            term += rf'instrument_platform="{self.fields["platform"]}" AND '
        if self.fields["selection"]:
            term += rf'library_selection="{self.fields["selection"]}" AND '
        if self.fields["source"]:
            term += rf'library_source="{self.fields["source"]}" AND '
        if self.fields["strategy"]:
            term += rf'library_strategy="{self.fields["strategy"]}" AND '
        if self.fields["title"]:
            term += rf'experiment_title="*{self.fields["title"]}*" AND '
        return term[:-5]  # Removing trailing " AND "

    def _format_request(self):
        # Note: ENA's API does not support searching a query in all fields.
        # Currently, if the user does not specify a query field, the query will
        # be matched to experiment_title (aka description),
        # or one of the accession fields
        stats_columns = ()
        payload = {
            "query": self._format_query_string(),
            "result": "read_run",
            "format": "json",
            "limit": self.return_max,
        }

        # Selects the fields to return at different verbosity levels
        if self.verbosity < 3:
            payload["fields"] = (
                "study_accession,"
                "experiment_accession,"
                "experiment_title,"
                "description,"
                "tax_id,"
                "scientific_name,"
                "library_strategy,"
                "library_source,"
                "library_selection,"
                "sample_accession,"
                "sample_title,"
                "instrument_model,"
                "run_accession,"
                "read_count,"
                "base_count,"
                "first_public,"
                "library_layout,"
                "instrument_platform"
            )
        elif self.verbosity == 3:
            payload["fields"] = "all"
        return payload

    def _format_result(self, content):
        if not content:
            return
        self.df = pd.DataFrame.from_dict(content).replace(r"^\s*$", pd.NA, regex=True)

        # Tabulate statistics
        self._update_stats()

        important_columns = [
            "study_accession",
            "experiment_accession",
            "experiment_title",
            "description",
            "tax_id",
            "scientific_name",
            "library_strategy",
            "library_source",
            "library_selection",
            "sample_accession",
            "sample_title",
            "instrument_model",
            "run_accession",
            "read_count",
            "base_count",
        ]

        if self.verbosity == 0:
            self.df = self.df[["run_accession"]]
        elif self.verbosity == 1:
            self.df = self.df[["run_accession", "description"]]
        elif self.verbosity == 2:
            self.df = self.df[important_columns]
        elif self.verbosity == 3:
            columns = list(self.df.columns)
            columns = important_columns + sorted(
                [col for col in columns if col not in important_columns]
            )
            self.df = self.df[columns]
        self.df.dropna(how="all")

    def _update_stats(self):
        # study
        self.stats["study"] = self.df["study_accession"].nunique()
        # experiment
        self.stats["experiment"] = self.df["experiment_accession"].nunique()
        # run
        self.stats["run"] = self.df["run_accession"].nunique()
        # sample
        self.stats["sample"] = self.df["sample_accession"].nunique()
        # date range
        daterange = self.df["first_public"]
        daterange = daterange[~pd.isna(daterange)]
        if not daterange.empty:
            dates = pd.to_datetime(daterange).dt.to_period("M").astype(str)
            self.stats["Date range"] = dates.value_counts().to_dict()
        # organisms
        organisms = self.df["scientific_name"]
        self.stats["Organisms"] = organisms.value_counts().to_dict()
        # strategy
        if "library_strategy" in self.df.columns:
            self.stats["Library strategy"] = (
                self.df["library_strategy"].value_counts().to_dict()
            )
        # source
        if "library_source" in self.df.columns:
            self.stats["Library source"] = (
                self.df["library_source"].value_counts().to_dict()
            )
        # selection
        if "library_selection" in self.df.columns:
            self.stats["Library selection"] = (
                self.df["library_selection"].value_counts().to_dict()
            )
        # layout
        if "library_layout" in self.df.columns:
            self.stats["Library layout"] = (
                self.df["library_layout"].value_counts().to_dict()
            )
        # platform
        if "instrument_platform" in self.df.columns:
            self.stats["Platform"] = (
                self.df["instrument_platform"].value_counts().to_dict()
            )
        # count
        count = self.df["base_count"].copy()
        count = count[~pd.isna(count)].astype("int64")
        self.stats["count_data"] = count
        self.stats["count_mean"] = count.mean()
        self.stats["count_median"] = count.median()
        self.stats["count_stdev"] = count.std()

        # For graphing
        self.stats["graph_raw"] = self.df[
            [
                "scientific_name",
                "library_strategy",
                "library_source",
                "library_selection",
                "first_public",
                "instrument_platform",
            ]
        ].rename(
            columns={
                "scientific_name": "Organism",
                "library_strategy": "Library Strategy",
                "library_source": "Library Source",
                "library_selection": "Library Selection",
                "first_public": "Publication Date",
                "instrument_platform": "Platform",
            }
        )
        self.stats["graph_raw"]["Publication Date"] = (
            pd.to_datetime(self.stats["graph_raw"]["Publication Date"])
            .dt.to_period("M")
            .astype(str)
        )


class GeoSearch(SraSearch):
    """Subclass of SraSearch that can query both GEO DataSets and SRA API.

    Methods
    -------
    search()
        sends the user query via requests to SRA, GEO DataSets, or both
        depending on the search query. If query is sent to both APIs,
        the intersection of the two sets of query results are returned.

    show_result_statistics()
        Shows summary information about search results.

    visualise_results()
        Generate graphs that visualise the search results.

    get_plot_objects():
        Get the plot objects for plots generated.

    _format_geo_query_string()
        formats the GEO DataSets portion of the input user query into a
        string.

    _format_geo_request()
        formats the GEO DataSets request payload

    _format_result(content)
        formats the search query output and converts it into a pandas
        dataframe

    See Also
    --------
    GeoSearch.info: GeoSearch usage details
    SraSearch: Superclass of GeoSearch
    QuerySearch: Superclass of SraSearch

    """

    def __init__(
        self,
        verbosity=2,
        return_max=20,
        query=None,
        accession=None,
        organism=None,
        layout=None,
        mbases=None,
        publication_date=None,
        platform=None,
        selection=None,
        source=None,
        strategy=None,
        title=None,
        geo_query=None,
        geo_dataset_type=None,
        geo_entry_type=None,
        suppress_validation=False,
    ):
        self.geo_fields = {
            "query": geo_query,
            "dataset_type": geo_dataset_type,
            "entry_type": geo_entry_type,
            "publication_date": publication_date,
            "organism": organism,
        }
        for k in self.geo_fields:
            if type(self.geo_fields[k]) == list:
                self.geo_fields[k] = " ".join(self.geo_fields[k])
        self.search_sra = True
        self.search_geo = True
        self.entries = {}
        self.number_entries = 0
        self.stats = {
            "study": "-",
            "experiment": "-",
            "run": "-",
            "sample": "-",
            "Date range": "-",
            "Organisms": "-",
            "Library strategy": "-",
            "Library source": "-",
            "Library selection": "-",
            "Library layout": "-",
            "Platform": "-",
            "count_mean": "-",
            "count_median": "-",
            "count_stdev": "-",
        }
        try:
            super().__init__(
                verbosity,
                return_max,
                query,
                accession,
                organism,
                layout,
                mbases,
                publication_date,
                platform,
                selection,
                source,
                strategy,
                title,
                suppress_validation,
            )
        except MissingQueryException:
            self.search_sra = False
        if not any(self.geo_fields.values()):
            self.search_geo = False
        if not self.search_geo and not self.search_sra:
            raise MissingQueryException()
        # Narrowing down the total number of eligible uids
        if self.fields["query"]:
            self.fields["query"] += " AND sra gds[Filter]"
        elif self.search_sra:
            self.fields["query"] = "sra gds[Filter]"
        if self.geo_fields["query"]:
            self.geo_fields["query"] += " AND gds sra[Filter]"
        elif self.search_geo:
            self.geo_fields["query"] = "gds sra[Filter]"

    def _format_geo_query_string(self):
        term = ""
        if self.geo_fields["query"]:
            term += self.geo_fields["query"] + " AND "
        if self.geo_fields["organism"]:
            term += self.geo_fields["organism"] + "[Organism] AND "
        if self.geo_fields["publication_date"]:
            dates = []
            for date in self.fields["publication_date"].split(":"):
                dates.append("/".join(date.split("-")[::-1]))
            term += ":".join(dates) + "[PDAT] AND "
        if self.geo_fields["dataset_type"]:
            term += self.geo_fields["dataset_type"] + "[DataSet Type] AND "
        if self.geo_fields["entry_type"]:
            term += self.geo_fields["entry_type"] + "[Entry Type] AND "
        return term[:-5]  # Removing trailing " AND "

    def _format_geo_request(self):
        payload = {
            "db": "gds",
            "term": self._format_geo_query_string(),
            "retmode": "json",
            "retmax": self.return_max * 10,
            "usehistory": "y",
        }
        return payload

    def _format_request(self):
        if not self.search_geo:
            retmax = self.return_max
        else:
            retmax = self.return_max * 10
        payload = {
            "db": "sra",
            "term": self._format_query_string(),
            "retmode": "json",
            "retmax": retmax,
        }
        return payload

    def search(self):
        if not self.search_geo:
            super().search()
        else:
            # Step 1: retrieves the list of uids from GEO DataSets, and use
            # ELink to find corresponding uids in SRA
            geo_payload = self._format_geo_request()
            try:
                r = requests_3_retries().get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                    params=geo_payload,
                    timeout=SEARCH_REQUEST_TIMEOUT,
                )
                r.raise_for_status()
                result = r.json()["esearchresult"]
                query_key = result["querykey"]
                web_env = result["webenv"]
                elink_payload = {
                    "dbfrom": "gds",
                    "db": "sra",
                    "retmode": "json",
                    "query_key": query_key,
                    "WebEnv": web_env,
                }
                r = requests_3_retries().get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi",
                    params=elink_payload,
                    timeout=SEARCH_REQUEST_TIMEOUT,
                )
                r.raise_for_status()
                try:
                    data = r.json()
                    uids_from_geo = data["linksets"][0]["linksetdbs"][0]["links"]
                except (JSONDecodeError, KeyError, IndexError):
                    uids_from_geo = []
                # Step 2: Retrieve list of uids from SRA and
                # Find the intersection of both lists of uids
                if self.search_sra:
                    r = requests_3_retries().get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                        params=self._format_request(),
                        timeout=SEARCH_REQUEST_TIMEOUT,
                    )
                    r.raise_for_status()
                    uids_from_sra = r.json()["esearchresult"]["idlist"]
                    uids = list(set(uids_from_sra).intersection(uids_from_geo))
                else:
                    uids = uids_from_geo
                # Ensure that only return_max number of uids are used
                uids = uids[: self.return_max]
                # Step 3: retrieves the detailed information for each uid
                # returned, in groups of SRA_SEARCH_GROUP_SIZE.
                if not uids:
                    print(
                        f"No results found for the following search query: \n "
                        f"SRA: {self.fields}\nGEO DataSets: {self.geo_fields}"
                    )
                    return  # If no queries found, return nothing
                pbar = tqdm(total=len(uids))
                for i in range(0, len(uids), SRA_SEARCH_GROUP_SIZE):
                    current_uids = ",".join(
                        uids[i : min(i + SRA_SEARCH_GROUP_SIZE, len(uids))]
                    )
                    pbar.update(min(SRA_SEARCH_GROUP_SIZE, len(uids) - i))
                    payload2 = {"db": "sra", "retmode": "xml", "id": current_uids}

                    r = requests_3_retries().get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                        params=payload2,
                        timeout=SEARCH_REQUEST_TIMEOUT,
                        stream=True,
                    )
                    r.raise_for_status()
                    r.raw.decode_content = True
                    self._format_response(r.raw)
                pbar.close()
                self._format_result()
            except requests.exceptions.Timeout:
                sys.exit(f"Connection to the server has timed out. Please retry.")
            except requests.exceptions.HTTPError:
                sys.exit(
                    f"HTTPError: This is likely caused by an invalid search query: "
                    f"\nURL queried: {r.url} \nUser query: {self.fields}"
                )

    @classmethod
    def info(cls):
        """Information on how to use GeoSearch.

        Displays information on how to query GEO DataSets / SRA via
        GeoSearch, including accepted inputs for geo_query,
        geo_dataset_type and geo_entry_type.

        Returns
        -------
        info: str
            Information on how to use GeoSearch.
        """
        info = (
            "General Information:\n"
            "--------------------\n"
            "GeoSearch (Or 'pysradb search --db geo ...' on the command line) \n"
            "is able to query both SRA and GEO DataSets, returning the subset \n"
            "of entries that appears within both search queries. \n\n"
            "Queries sent to SRA and GEO DataSets will have 'sra gds[Filter]' \n"
            "and 'gds sra[Filter]' appended to the search queries respectively \n"
            "to ensure that the entries in the search result can also be found \n"
            "in the other API. \n\n"
            "Queries sent to SRA uses the same fields as SraSearch, \n"
            "or 'pysradb search --db sra ...' on the command line. \n\n"
            "The following fields, if used, are sent as part of the GEO DataSets query: \n"
            "organism, publication_date, geo_query, geo_dataset_type, geo_entry_type\n\n"
            "Notes about GEO DataSets specific fields: \n"
            "----------------------------------------- \n"
            "geo_query: This is the free text query, similar to 'query', that \n"
            "is sent to GEO DataSets API. The 'query' field is the free text \n"
            "query sent to SRA API instead.\n\n"
            "geo_dataset_type: The type of GEO DataSet, which can be one of the following: \n"
            "  expression profiling by array \n"
            "  expression profiling by genome tiling array \n"
            "  expression profiling by high throughput sequencing \n"
            "  expression profiling by mpss \n"
            "  expression profiling by rt pcr \n"
            "  expression profiling by sage \n"
            "  expression profiling by snp array \n"
            "  genome binding/occupancy profiling by array \n"
            "  genome binding/occupancy profiling by genome tiling array \n"
            "  genome binding/occupancy profiling by high throughput sequencing \n"
            "  genome binding/occupancy profiling by snp array \n"
            "  genome variation profiling by array \n"
            "  genome variation profiling by genome tiling array \n"
            "  genome variation profiling by high throughput sequencing \n"
            "  genome variation profiling by snp array \n"
            "  methylation profiling by array \n"
            "  methylation profiling by genome tiling array \n"
            "  methylation profiling by high throughput sequencing \n"
            "  methylation profiling by snp array \n"
            "  non coding rna profiling by array \n"
            "  non coding rna profiling by genome tiling array \n"
            "  non coding rna profiling by high throughput sequencing \n"
            "  other \n"
            "  protein profiling by mass spec \n"
            "  protein profiling by protein array \n"
            "  snp genotyping by snp array \n"
            "  third party reanalysis\n\n"
            "geo_dataset_type: The type of GEO entry, which can be one of the following: \n"
            "  gds\n"
            "  gpl\n"
            "  gse\n"
            "  gsm\n\n"
        )

        return info

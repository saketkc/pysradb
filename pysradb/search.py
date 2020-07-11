"""This file contains the search classes for the search feature.
"""

import re
import requests
import sys
import urllib
import pandas as pd
import xml.etree.ElementTree as Et
from json import JSONDecodeError
from tqdm import tqdm

from .exceptions import IncorrectFieldException
from .exceptions import MissingQueryException
from .utils import scientific_name_to_taxid, requests_3_retries

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
    fields : dict
        The fields supplied for the query. If all fields are empty, raises
        MissingQueryException.

    Methods
    -------
    get_df()
        Returns the dataframe storing this search result

    """

    def __init__(self, verbosity, return_max, fields):
        self.verbosity = verbosity
        self.return_max = return_max
        allowed_fields = [
            "query",
            "accession",
            "organism",
            "layout",
            "mbases",
            "publication_date",
            "platform",
            "selection",
            "source",
            "strategy",
            "title",
        ]
        for field in allowed_fields:
            if field not in fields:
                fields[field] = None
        for k in fields:
            if type(fields[k]) == list:
                fields[k] = " ".join(fields[k])
        if not any(fields):
            raise MissingQueryException()
        self.fields = fields
        self.df = pd.DataFrame()

    def _validate_fields(self):
        # TODO: validate the contents of all the fields here
        pass

    def search(self):
        pass

    def get_df(self):
        return self.df.replace(r"^\s*$", "N/A", regex=True)


class SraSearch(QuerySearch):
    """Subclass of QuerySearch that implements search by querying
    NCBI Entrez API

    Methods
    -------
    search()
        sends the user query via requests to NCBI Entrez API and returns
        search results as a pandas dataframe.

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

    def search(self):
        # Step 1: retrieves the list of uids that satisfies the input
        # search query
        entries = {}
        number_entries = 0
        payload = self._format_request()
        try:
            r = requests_3_retries().get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params=payload,
                timeout=SEARCH_REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            uids = r.json()["esearchresult"]["idlist"]

            # Step 2: retrieves the detailed information for each uid returned, in groups of 300.
            if not uids:
                print(
                    f"No results found for the following search query: \n {self.fields}"
                )
                return  # If no queries found, return nothing

            pbar = tqdm(total=len(uids))
            for i in range(0, len(uids), SRA_SEARCH_GROUP_SIZE):
                current_uids = ",".join(uids[i: min(i + SRA_SEARCH_GROUP_SIZE, len(uids))])
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
                field_categories = ["EXPERIMENT", "SUBMISSION", "ORGANISATION", "STUDY", "SAMPLE", "Pool", "RUN_SET"]
                for event, elem in Et.iterparse(r.raw):
                    if elem.tag == "EXPERIMENT_PACKAGE":
                        number_entries += 1
                    elif elem.tag in field_categories:
                        self._parse_entry(elem, entries, number_entries)
            pbar.close()
        except requests.exceptions.Timeout:
            sys.exit(f"Connection to the server has timed out. Please retry.")
        except requests.exceptions.HTTPError:
            sys.exit(
                f"HTTPError: This is likely caused by an invalid search query: "
                f"\nURL queried: {r.url} \nUser query: {self.fields}"
            )
        finally:
            for field in entries:
                if len(entries[field]) < number_entries:
                    entries[field] += [""] * (number_entries - len(entries[field]))
            self.df = pd.DataFrame.from_dict(entries)
            self._format_result()

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
            if type(self.fields["mbases"]) != int:
                raise IncorrectFieldException(
                    f"Incorrect mbases format: {self.fields['mbases']}\n"
                    f"--mbases must be an integer"
                )
            term += self.fields["mbases"] + "[Mbases] AND "
        if self.fields["publication_date"]:
            for date in self.fields["publication_date"].split(":"):
                if not re.match(
                    "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(19|20)[0-9]{2}$", date
                ):
                    raise IncorrectFieldException(
                        f"Incorrect publication date format: {self.fields['publication_date']}\n"
                        f"Expected format: dd-mm-yyyy or dd-mm-yyyy:dd-mm-yyyy, between 1900-2099"
                    )
            term += self.fields["publication_date"].replace("-", "/") + "[PDAT] AND "
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

    def _format_result(self):
        if self.df.empty:
            return
        columns = list(self.df.columns)
        important_columns = [
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
        for col in important_columns:
            if col not in columns:
                important_columns.remove(col)
            else:
                columns.remove(col)

        if self.verbosity == 0:
            self.df = self.df[["run_1_accession"]]
        elif self.verbosity == 1:
            if "experiment_title" not in self.df.columns:
                self.df = self.df[["run_1_accession"]]
            else:
                self.df = self.df[["run_1_accession", "experiment_title"]]
        elif self.verbosity == 2:
            self.df = self.df[important_columns]
        elif self.verbosity == 3:
            self.df = self.df[important_columns + sorted(columns)]
        self.df.dropna(how="all")

    def _parse_entry(self, entry_root, entries, number_entries):
        """Parses a subset of the XML tree from request stream

        Parameters
        ----------
        entry_root: ElementTree.Element
            root element of the xml tree from requests stream
        entries: dict
            python dictionary of lists, containing the entry information
            from the search results
        number_entries: int
            The number of entries that has been processed. This is used
            to pad lists in the dictionary with empty strings, for entries
            missing certain fields

        """
        field_header = entry_root.tag.lower()
        run_count = 0

        # root element attributes
        for k, v in entry_root.attrib.items():
            self._update_entry(
                entries,
                f"{field_header}_{k}".lower(),
                v,
                number_entries
            )

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
                            entries,
                            f"{field_header}_external_id_{id_index}",
                            identifier.text,
                            number_entries
                        )
                        self._update_entry(
                            entries,
                            f"{field_header}_external_id_{id_index}_namespace",
                            identifier.get("namespace"),
                            number_entries
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
                        entries,
                        f"{link.tag}_{link_index}_type".lower(),
                        link[0].tag,
                        number_entries
                    )
                    # Link values in the form of tag: value.
                    # Eg: label: GEO sample
                    link_value_index = 1
                    for link_value in link[0]:
                        self._update_entry(
                            entries,
                            f"{link.tag}_{link_index}_value_{link_value_index}".lower(),
                            f"{link_value.tag}: {link_value.text}",
                            number_entries
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
                            entries,
                            f"{child.tag}_{attribute_index}_{val.tag}".lower(),
                            val.text,
                            number_entries
                        )
                    attribute_index += 1

            # Differentiating between sample title and experiment title.
            elif child.tag == "TITLE":
                self._update_entry(
                    entries,
                    f"{field_header}_title",
                    child.text,
                    number_entries
                )

            # Parsing platfrom information
            elif child.tag == "PLATFORM":
                platform = child[0]
                self._update_entry(
                    entries,
                    "experiment_platform",
                    platform.tag,
                    number_entries
                )
                self._update_entry(
                    entries,
                    "experiment_instrument_model",
                    platform[0].text,
                    number_entries
                )

            # Parsing individual run information
            elif child.tag == "RUN":
                run_count += 1
                # run attributes
                for k, v in child.attrib.items():
                    self._update_entry(
                        entries,
                        f"run_{run_count}_{k}".lower(),
                        v,
                        number_entries
                    )

                for elem in child:
                    if elem.tag == "SRAFiles":
                        srafile_index = 1
                        for srafile in elem:
                            for k, v in srafile.attrib.items():
                                self._update_entry(
                                    entries,
                                    f"run_{run_count}_srafile_{srafile_index}_{k}".lower(),
                                    v,
                                    number_entries
                                )
                            alternatives_index = 1
                            for alternatives in srafile:
                                for k, v in alternatives.attrib.items():
                                    self._update_entry(
                                        entries,
                                        f"run_{run_count}_srafile_{srafile_index}_alternative_{alternatives_index}_{k}".lower(),
                                        v,
                                        number_entries
                                    )
                                alternatives_index += 1
                            srafile_index += 1

                    elif elem.tag == "CloudFiles":
                        cloudfile_index = 1
                        for cloudfile in elem:
                            for k, v in cloudfile.attrib.items():
                                self._update_entry(
                                    entries,
                                    f"run_{run_count}_cloudfile_{cloudfile_index}_{k}".lower(),
                                    v,
                                    number_entries
                                )
                            cloudfile_index += 1

                    elif elem.tag == "Bases":
                        for k, v in elem.attrib.items():
                            self._update_entry(
                                entries,
                                f"run_{run_count}_total_base_{k}".lower(),
                                v,
                                number_entries
                            )
                        for base in elem:
                            self._update_entry(
                                entries,
                                f"run_{run_count}_base_{base.attrib['value']}_count",
                                base.attrib['count'],
                                number_entries
                            )

                    elif elem.tag == "Databases":
                        database_index = 1
                        for database in elem:
                            self._update_entry(
                                entries,
                                f"run_{run_count}_database_{database_index}".lower(),
                                Et.tostring(database).decode(),
                                number_entries
                            )
                            database_index += 1

            else:
                for elem in child.iter():
                    # Tags to ignore to avoid confusion
                    if elem.tag in ["PRIMARY_ID", "SINGLE", "PAIRED"]:
                        continue
                    elif elem.text:
                        self._update_entry(
                            entries,
                            f"{field_header}_{elem.tag.lower()}",
                            elem.text,
                            number_entries
                        )
                    elif elem.attrib:
                        for k, v in elem.attrib.items():
                            self._update_entry(
                                entries,
                                f"{field_header}_{elem.tag}_{k}".lower(),
                                v,
                                number_entries
                            )

            # Parsing library layout (single, paired)
            if field_header == "experiment":
                library_layout = child.find("./DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_LAYOUT")
                if library_layout:
                    library_layout = library_layout[0]
                    self._update_entry(
                        entries,
                        f"library_layout",
                        library_layout.tag,
                        number_entries
                    )
                    # If library layout is paired, information such as nominal
                    # standard deviation and length, etc are provided as well.
                    if library_layout.tag == "PAIRED":
                        for k, v in library_layout.attrib.items():
                            self._update_entry(
                                entries,
                                f"library_layout_{k}".lower(),
                                v,
                                number_entries
                            )

    def _update_entry(self, entries, field_name, field_content, number_entries):
        """Adds information from a field into the entries dictionary

        This is a helper function that adds information parsed from the XML
        output from SRA into a dictionary of lists, for easier conversion
        into a Pandas dataframe later. Dictionary key is created if it
        doesn't exist yet. For entries that does not have information
        belonging to a field, the corresponding list will be padded with
        empty strings.

        Parameters
        ----------
        entries: dict
            python dictionary of lists, containing the entry information
            from the search results
        field_name: str
            Name of the field where a value belonging to an entry is to be
            added
        field_content: str
            Value to be added
        number_entries: int
            The number of entries that has been processed. This is used
            to pad lists in the dictionary with empty strings, for entries
            missing certain fields
        """
        if field_name not in entries:
            entries[field_name] = []
        if len(entries[field_name]) > number_entries:
            return
        entries[field_name] += [""] * (number_entries - len(entries[field_name])) + [field_content]


class EnaSearch(QuerySearch):
    """Subclass of QuerySearch that implements search via querying ENA API


    Methods
    -------
    search()
        sends the user query via requests to ENA API and stores search
        result as an instance attribute in the form of a pandas dataframe

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
            term += rf'experiment_title="*{self.fields["query"]}*" OR '
            if not self.fields["accession"]:
                self.fields["query"] = self.fields["query"].upper()
                term += (
                    rf'(study_accession="{self.fields["query"]}" OR '
                    rf'secondary_study_accession="{self.fields["query"]}" OR '
                    rf'sample_accession="{self.fields["query"]}" OR '
                    rf'secondary_sample_accession="{self.fields["query"]}" OR '
                    rf'experiment_accession="{self.fields["query"]}" OR '
                    rf'submission_accession="{self.fields["query"]}" OR '
                    rf'run_accession="{self.fields["query"]}") AND '
                )
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
                if not re.match(
                    "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(19|20)[0-9]{2}$",
                    dates[i],
                ):
                    raise IncorrectFieldException(
                        f"Incorrect publication date format: {self.fields['publication_date']}\n"
                        f"Expected format: dd-mm-yyyy or dd-mm-yyyy:dd-mm-yyyy, between 1900-2099"
                    )
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
            term += rf'instrument_platform="{self.fields["platform"].upper()}" AND '
        if self.fields["selection"]:
            term += rf'library_selection="{self.fields["selection"].upper()}" AND '
        if self.fields["source"]:
            term += rf'library_source="{self.fields["source"].upper()}" AND '
        if self.fields["strategy"]:
            term += rf'library_strategy="{self.fields["strategy"].upper()}" AND '
        if self.fields["title"]:
            term += rf'experiment_title="*{self.fields["title"]}*" AND '
        return term[:-5]  # Removing trailing " AND "

    def _format_request(self):
        # Note: ENA's API does not support searching a query in all fields.
        # Currently, if the user does not specify a query field, the query will
        # be matched to experiment_title (aka description),
        # or one of the accession fields
        payload = {
            "dataPortal": "ena",
            "query": self._format_query_string(),
            "result": "read_run",
            "format": "json",
            "limit": self.return_max,
        }

        # Selects the exact fields to return at different verbosity levels
        if self.verbosity == 0:
            payload["fields"] = "run_accession"
        elif self.verbosity == 1:
            pass  # default, fields = "run_accession,description"
        elif self.verbosity == 2:
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
                "base_count"
            )
        elif self.verbosity == 3:
            payload["fields"] = "all"

        return payload

    def _format_result(self, content):
        if not content:
            return
        self.df = pd.DataFrame.from_dict(content)
        if self.verbosity == 3:
            columns = list(self.df.columns)
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
            columns = important_columns + sorted(
                [col for col in columns if col not in important_columns]
            )
            self.df = self.df[columns]
        self.df.dropna(how="all")


class GeoSearch(SraSearch):
    # TODO: extend SraSearch by searching Geo db for uids/accessions to
    #  match first
    def __init__(self, verbosity, return_max, fields):
        super().__init__(verbosity, return_max, fields)

    def search(self):
        super().search()

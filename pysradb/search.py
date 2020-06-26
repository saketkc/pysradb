"""This file contains the search classes for the search feature.
"""

import re
import requests
import urllib
import pandas as pd
import xml.etree.ElementTree as Et
from collections import OrderedDict
from json import JSONDecodeError

from .exceptions import MissingQueryException, IncorrectFieldException
from .utils import scientific_name_to_taxid


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
        for k in fields:
            if type(fields[k]) == list:
                fields[k] = " ".join(fields[k])
        if not any(fields):
            raise MissingQueryException()
        self.fields = fields
        self.df = pd.DataFrame()

    def search(self):
        pass

    def get_df(self):
        return self.df


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

        payload = self._format_request()
        try:
            r = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params=OrderedDict(payload),
                timeout=20,
            )
            r.raise_for_status()
            uids = r.json()["esearchresult"]["idlist"]

            # Step 2: retrieves the detailed information for each uid returned, in groups of 500.
            if not uids:
                print(
                    f"No results found for the following search query: \n {self.fields}"
                )
                return  # If no queries found, return nothing

            for i in range(0, len(uids), 300):
                current_uids = ",".join(uids[i : min(i + 300, len(uids))])

                payload2 = {"db": "sra", "retmode": "xml", "id": current_uids}

                r = requests.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                    params=OrderedDict(payload2),
                    timeout=20,
                )
                r.raise_for_status()
                self._format_result(r.content)
        except requests.exceptions.Timeout:
            print(f"Connection to the server has timed out. Please retry.")
            return
        except requests.exceptions.HTTPError:
            print(
                f"HTTPError: This is likely caused by an invalid search query: "
                f"\nURL queried: {r.url} \nUser query: {self.fields}"
            )
            return

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

    def _format_result(self, content):
        if not content:
            return
        root = Et.fromstring(content)

        for entry in root:  # for each result entry
            fields = {}
            for child in entry.iter():
                if child.text:
                    fields[child.tag.lower()] = child.text
                if child.attrib:
                    for k, v in child.attrib.items():
                        fields[(child.tag + "_" + k).lower()] = v
            self.df = self.df.append(fields, ignore_index=True)

        if self.df.empty:
            return
        columns = list(self.df.columns)
        important_columns = [
            "experiment_accession",
            "title",
            "design_description",
            "member_tax_id",
            "member_organism",
            "library_strategy",
            "library_source",
            "library_selection",
            "sample_accession",
            "sample_alias",
            "instrument_model",
            "member_spots",
            "run_size",
            "run_accession",
            "run_total_spots",
            "run_total_bases",
        ]
        for col in important_columns:
            if col not in columns:
                important_columns.remove(col)
            else:
                columns.remove(col)

        if self.verbosity == 0:
            self.df = self.df[["run_accession"]]
        elif self.verbosity == 1:
            if "design_description" not in self.df.columns:
                self.df = self.df[["run_accession"]]
            else:
                self.df = self.df[["run_accession", "design_description"]]
        elif self.verbosity == 2:
            self.df = self.df[important_columns]
        elif self.verbosity == 3:
            self.df = self.df[important_columns + sorted(columns)]
        self.df.dropna(how="all")


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
            r = requests.get(
                "https://www.ebi.ac.uk/ena/portal/api/search",
                params=payload,
                timeout=20,
            )
            r.raise_for_status()
            self._format_result(r.json())
        except requests.exceptions.Timeout:
            print(f"Connection to the server has timed out. Please retry.")
            return
        except requests.exceptions.HTTPError:
            print(
                f"HTTPError: This is likely caused by an invalid search query: "
                f"\nURL queried: {r.url} \nUser query: {self.fields}"
            )
            return
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

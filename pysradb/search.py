"""This file contains the search classes for the search feature.
"""

import requests
import urllib
import pandas as pd
import xml.etree.ElementTree as Et
from collections import OrderedDict


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
    search_text : string
        The base search query string.
    verbosity : integer
        The level of details of the search result.
    platform : string
        The sequencing platform used.

    Methods
    -------
    get_df()
        Returns the dataframe storing this search result

    """

    def __init__(self, search_text, verbosity, platform):
        self.search_text = search_text
        self.verbosity = verbosity
        self.platform = platform
        self.df = pd.DataFrame()
        self._search()

    def _search(self):
        pass

    def get_df(self):
        return self.df


class SraSearch(QuerySearch):
    """Subclass of QuerySearch that implements search by querying
    NCBI Entrez API

    Methods
    -------
    _search()
        sends the user query via requests to NCBI Entrez API and returns
        search results as a pandas dataframe.

    _format_query()
        formats the input user query.

    _format_result(content)
        formats the search query output.

    See Also
    --------
    QuerySearch: Superclass of SraSearch

    """

    def _search(self):
        # Step 1: retrieves the list of uids that satisfies the input
        # search query

        # This ensures that the spaces in the query string are not
        # converted to '+' by requests.
        payload = self._format_query()

        r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=OrderedDict(payload))
        r.raise_for_status()
        uids = r.json()["esearchresult"]["idlist"]

        # Step 2: retrieves the detailed information for each of the uids.
        if not uids:
            return
        uids = ",".join(uids)

        payload2 = {
            "db": "sra",
            "retmode": "xml",
            "id": uids
        }

        r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=OrderedDict(payload2))
        r.raise_for_status()
        self._format_result(r.content)

    def _format_query(self):
        payload = {
            "db": "sra",
            "term": self.search_text,
            "retmode": "json",
            "retmax": 200  # for testing purposes

        }
        if self.platform:
            payload["term"] += f' AND "{self.platform}"[platform]'
        return payload

    def _format_result(self, content):
        root = Et.fromstring(content)
        for run in root.iter("RUN"):
            self.df = self.df.append(run.attrib, ignore_index=True)


class EnaSearch(QuerySearch):
    """Subclass of QuerySearch that implements search via querying ENA API


    Methods
    -------
    _search()
        sends the user query via requests to ENA API and stores search
        result as an instance attribute in the form of a pandas dataframe

    _format_query()
        formats the input user query

    _format_result(content)
        formats the search query output and converts it into a pandas
        dataframe

    See Also
    --------
    QuerySearch: Superclass of EnaSearch

    """

    def _search(self):
        # This ensures that the spaces in the query string are not
        # converted to '+' by requests.
        payload = urllib.parse.urlencode(self._format_query(), quote_via=urllib.parse.quote)

        r = requests.get("https://www.ebi.ac.uk/ena/portal/api/search", params=payload)
        r.raise_for_status()
        self._format_result(r.json())

    def _format_query(self):
        # Note: ENA's API does not support searching a query in all fields.
        # Currently, if the user does not specify a query field, the query will
        # be searched in study_title, sample_title, or experiment_title
        payload = {
            "dataPortal": "ena",
            "query": rf'(study_title="*{self.search_text}*" OR sample_title="*{self.search_text}*" OR '
                     rf'experiment_title="*{self.search_text}*") ',
            "result": "read_run",
            "format": "json",
            "limit": 200  # for testing purposes
        }

        if self.platform:
            payload["query"] += rf'AND instrument_platform="{self.platform.upper()}"'

        # This can be expanded to select the exact fields of attributes to
        # return at different verbosity levels
        if self.verbosity == 1:
            payload["fields"] = "all"

        return payload

    def _format_result(self, content):
        return pd.DataFrame.from_dict(content)

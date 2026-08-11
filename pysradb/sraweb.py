"""Utilities to interact with SRA online"""

import concurrent.futures
import json
import os
import re
import sys
import time
import warnings
from collections import OrderedDict
from json.decoder import JSONDecodeError
from xml.etree import ElementTree as ET
from xml.parsers.expat import ExpatError
from xml.sax.saxutils import escape

import pandas as pd
import requests
import xmltodict

from .download import download_file, get_file_size
from .search import SraSearch
from .utils import confirm

warnings.simplefilter(action="ignore", category=FutureWarning)


class OpenAlexError(RuntimeError):
    """Raised when OpenAlex API returns a non-transient error (rate limit, auth, etc.)."""

    pass


def xmlescape(data):
    return escape(data, entities={"'": "&apos;", '"': "&quot;"})


def _make_hashable(obj):
    """Convert unhashable types to hashable ones for pandas operations"""
    if isinstance(obj, (OrderedDict, dict)):
        # Extract text content from XML parsed dict/OrderedDict
        if "#text" in obj:
            return obj["#text"]  # Extract the actual text content
        elif len(obj) == 1 and "@xmlns" in obj:
            return pd.NA  # Handle xmlns-only dicts as missing data
        else:
            # Fallback to string representation for other dict structures
            return str(obj)
    elif isinstance(obj, list):
        # Convert list to tuple
        return tuple(_make_hashable(item) for item in obj)
    else:
        return obj


def _order_first(df, column_order_list):
    columns = column_order_list + [
        col for col in df.columns.tolist() if col not in column_order_list
    ]
    # check if all columns do exist in the dataframe
    if len(set(columns).intersection(df.columns)) == len(columns):
        df = df.loc[:, columns]
    df = df.mask(df.map(str).eq("[]"))
    # Filter out XML namespace artifacts
    df = df.replace(regex=r"^@xmlns.*", value=pd.NA).infer_objects(copy=False)
    df = df.fillna(pd.NA)
    return df


def _retry_response(base_url, payload, key, max_retries=10):
    """Rerty fetching esummary if API rate limit exceeeds"""
    for index, _ in enumerate(range(max_retries)):
        try:
            request = requests.get(base_url, params=OrderedDict(payload))
            response = request.json()
            _ = response[key]
            return response
        except (KeyError, ValueError, requests.RequestException):
            # missing key, bad body (5xx), or network error -> back off
            time.sleep(index + 1)
            continue
    raise RateLimitError("Failed to fetch esummary. API rate limit exceeded.")


class TransientAPIError(BaseException):
    """BaseException so ``except Exception`` can't swallow it into a NULL result."""


class RateLimitError(TransientAPIError):
    """NCBI/EBI 429/503 or rate-limit body."""


class ServerError(TransientAPIError):
    """NCBI/EBI 5xx, timeout, or connection error."""


def get_retmax(n_records, retmax=500):
    """Get retstart and retmax till n_records are exhausted"""
    for i in range(0, n_records, retmax):
        yield i


TRUNCATED_TITLE_LENGTH = 80


class SRAweb(object):
    def __init__(
        self,
        api_key: str | None = None,
        openalex_api_key: str | None = None,
        openalex_email: str | None = None,
        retries: int = 3,
        timeout: int = 60,
        verbose=True,
    ):
        """
        Initialize SRAweb for API-based access to SRA data.

        Parameters
        ----------

        api_key: string
                 API key for ncbi eutils. Optional, but recommended for higher rate limits.
        openalex_api_key: string
                 API key for OpenAlex.
                 Get a free key at https://openalex.org/settings/api
                 Falls back to OPENALEX_API_KEY environment variable.
        openalex_email: string
                 Email for OpenAlex polite pool (higher rate limits).
                 Falls back to OPENALEX_EMAIL environment variable.
        retries: int
                 Number of retries for failed HTTP requests. Default 3.
        timeout: int
                 Timeout in seconds for HTTP requests. Default 60.
        verbose: bool
                 Print warning/info messages. Default True.
        """
        self.base_url = dict()
        self.base_url["esummary"] = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        )
        self.base_url["esearch"] = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        self.base_url["efetch"] = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        )

        self.base_url["europepmc"] = (
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        )

        self.ena_fastq_search_url = "https://www.ebi.ac.uk/ena/portal/api/filereport"
        self.ena_params = [("result", "read_run"), ("fields", "fastq_ftp")]
        self.pysraweb_api_url = os.environ.get(
            "PYSRAWEB_API_URL", "https://pysraweb.saketlab.org/api"
        )

        self.esearch_params = {}
        self.esearch_params["sra"] = [
            ("db", "sra"),
            ("usehistory", "n"),
            ("retmode", "json"),
        ]
        self.esearch_params["geo"] = [
            ("db", "gds"),
            ("usehistory", "n"),
            ("retmode", "json"),
        ]
        self.efetch_params = [
            ("db", "sra"),
            ("usehistory", "n"),
            ("retmode", "runinfo"),
        ]

        self.api_key = str(api_key) if api_key is not None else None
        if self.api_key:
            self.esearch_params["sra"].append(("api_key", self.api_key))
            self.esearch_params["geo"].append(("api_key", self.api_key))
            self.efetch_params.append(("api_key", self.api_key))
            self.sleep_time = 1 / 10
        else:
            self.sleep_time = 1 / 3

        self.openalex_api_key = openalex_api_key or os.environ.get("OPENALEX_API_KEY")
        self.openalex_email = openalex_email or os.environ.get("OPENALEX_EMAIL")
        self.verbose = verbose
        self.retries = retries
        self.timeout = timeout

    @staticmethod
    def format_xml(string):
        """Create a fake root to make 'string' a valid xml

        Parameters
        ----------
        string : str

        Returns
        -------
        str
        """
        # string = unescape(string.strip())
        string = string.strip()
        return "<root>" + string + "</root>"

    @staticmethod
    def xml_to_json(xml):
        """Convert xml to json.

        Parameters
        ----------
        xml: str
             Input XML

        Returns
        -------
        xml_dict: dict
                  Parsed xml as dict
        """
        try:
            xmldict = xmltodict.parse(
                xml, process_namespaces=False, dict_constructor=OrderedDict
            )
            json = xmldict["root"]
        except ExpatError:
            raise RuntimeError("Unable to parse xml: {}".format(xml))
        return json

    def bioproject_to_srp(self, bioproject):
        """Convert PRJNA BioProject ID to SRP accession

        Parameters
        ----------
        bioproject: str
                   BioProject ID (e.g., 'PRJNA810439')

        Returns
        -------
        srp_accessions: list
                       List of SRP accessions found
        """
        if not bioproject or pd.isna(bioproject):
            return []

        try:
            import re

            # Search SRA for records with this bioproject
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "sra",
                "term": f"{bioproject}[BioProject]",
                "retmode": "json",
                "retmax": "50",
            }

            response = self._send_retryable_request(
                search_url,
                params=search_params,
            )
            result = response.json()
            sra_uids = result.get("esearchresult", {}).get("idlist", [])

            if not sra_uids:
                return []

            # Get summaries to extract SRP accessions
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            srp_set = set()

            # Process in batches to avoid too many requests
            for uid in sra_uids[:10]:  # Limit to first 10
                try:
                    summary_params = {"db": "sra", "id": uid, "retmode": "json"}
                    summary_response = self._send_retryable_request(
                        summary_url,
                        params=summary_params,
                        retries=self.retries,
                        timeout=self.timeout,
                    )
                    summary_result = summary_response.json()

                    if uid in summary_result.get("result", {}):
                        record = summary_result["result"][uid]
                        expxml = record.get("expxml", "")

                        # Extract SRP using regex from the XML
                        srp_match = re.search(r'Study acc="(SRP\d+)"', expxml)
                        if srp_match:
                            srp_set.add(srp_match.group(1))

                    time.sleep(0.1)  # Small delay between requests
                except Exception:
                    continue

            return sorted(list(srp_set))

        except Exception:
            return []

    def fetch_ena_fastq(self, srp):
        """Fetch FASTQ records from ENA (EXPERIMENTAL)

        Parameters
        ----------
        srp: string
             Srudy accession

        Returns
        -------
        srr_url: list
                 List of SRR fastq urls
        """
        payload = self.ena_params.copy()
        payload += [("accession", srp)]
        request = self._send_retryable_request(
            self.ena_fastq_search_url, params=OrderedDict(payload)
        )
        request_text = request.text.strip()
        urls = []
        for line in request_text.split("\n"):
            if "fastq_ftp" in line:
                continue
            line = line.strip()
            line_split = line.split("\t")
            if len(line_split) != 2:
                continue
            url, srr = line.split("\t")
            # sometimes this needs to be flipped
            if "sra.ebi.ac.uk" in srr:
                url, srr = srr, url
            http_url = "http://{}".format(url)
            ftp_url = url.replace("ftp.sra.ebi.ac.uk/", "era-fasp@fasp.sra.ebi.ac.uk:")
            urls += [(srr, http_url, ftp_url)]

        # Paired end case
        def _handle_url_split(url_split):
            url1_1 = pd.NA
            url1_2 = pd.NA
            for url_temp in url_split:
                if "_1.fastq.gz" in url_temp:
                    url1_1 = url_temp
                elif "_2.fastq.gz" in url_temp:
                    url1_2 = url_temp
            return url1_1, url1_2

        if ";" in request_text:
            urls_expanded = []
            for srr, url1, url2 in urls:
                # strip _1, _2
                srr = srr.split("_")[0]
                if ";" in url1:
                    url1_split = url1.split(";")
                    if len(url1_split) == 2:
                        url1_1, url1_2 = url1_split
                    else:
                        # warnings.warn('ignoring extra urls found for paired end accession')
                        url1_1, url1_2 = _handle_url_split(url1_split)
                    url1_2 = "http://{}".format(url1_2)
                    url2_split = url2.split(";")
                    if len(url2_split) == 2:
                        url2_1, url2_2 = url2_split
                    else:
                        # warnings.warn('ignoring extra urls found for paired end accession')
                        url2_1, url2_2 = _handle_url_split(url2_split)
                else:
                    url1_1 = url1
                    url2_1 = url2
                    url1_2 = ""
                    url2_2 = ""
                urls_expanded.append((srr, url1_1, url1_2, url2_1, url2_2))
            df = pd.DataFrame(
                urls_expanded,
                columns=[
                    "run_accession",
                    "ena_fastq_http_1",
                    "ena_fastq_http_2",
                    "ena_fastq_ftp_1",
                    "ena_fastq_ftp_2",
                ],
            ).sort_values(by="run_accession")
            return df
        else:
            return pd.DataFrame(
                urls, columns=["run_accession", "ena_fastq_http", "ena_fastq_ftp"]
            ).sort_values(by="run_accession")

    def create_esummary_params(self, esearchresult, db="sra"):
        query_key = esearchresult["querykey"]
        webenv = esearchresult["webenv"]
        retstart = esearchresult["retstart"]

        # TODO this should be adaptive to build
        # upon using the 'count' result in esearch result,
        # Currently only supports a max of 500 records.
        # retmax = esearchresult["retmax"]
        retmax = 500

        return [
            ("query_key", query_key),
            ("WebEnv", webenv),
            ("retstart", retstart),
            ("retmax", retmax),
        ]

    def get_esummary_response(self, db, term, usehistory="y"):
        assert db in ["sra", "geo"]

        payload = self.esearch_params[db].copy()
        if isinstance(term, list):
            term = " OR ".join(term)
        payload += [("term", term)]
        request = self._send_retryable_request(
            self.base_url["esearch"], data=OrderedDict(payload), method="post"
        )
        try:
            esearch_response = request.json()
        except JSONDecodeError:
            if self.verbose:
                sys.stderr.write(
                    "Unable to parse esummary response json: {}{}. Will retry once.".format(
                        request.text, os.linesep
                    )
                )

            retry_after = request.headers.get("Retry-After", 1)
            time.sleep(int(retry_after))
            request = self._send_retryable_request(
                self.base_url["esearch"], data=OrderedDict(payload), method="post"
            )
            try:
                esearch_response = request.json()
            except JSONDecodeError as e:
                if self.verbose:
                    error_msg = "Unable to parse esummary response json: {}{}. Aborting.".format(
                        request.text, os.linesep
                    )
                    if self.verbose:
                        sys.stderr.write(error_msg)

                raise ValueError(error_msg) from e

            # retry again

        if "esummaryresult" in esearch_response:
            if self.verbose:
                print("No result found")
            return
        if "error" in esearch_response:
            # API rate limite exceeded
            esearch_response = _retry_response(
                self.base_url["esearch"],
                payload,
                "esearchresult",
                max_retries=self.retries,
            )

        n_records = int(esearch_response["esearchresult"]["count"])

        results = {}
        for retstart in get_retmax(n_records):
            payload = self.esearch_params[db].copy()
            payload += self.create_esummary_params(esearch_response["esearchresult"])
            payload = OrderedDict(payload)
            payload["retstart"] = retstart
            request = self._send_retryable_request(
                self.base_url["esummary"], params=OrderedDict(payload)
            )
            try:
                response = request.json()
            except JSONDecodeError:
                time.sleep(1)
                response = _retry_response(
                    self.base_url["esummary"],
                    payload,
                    "result",
                    max_retries=self.retries,
                )

            if "error" in response:
                # API rate limite exceeded
                response = _retry_response(
                    self.base_url["esummary"],
                    payload,
                    "result",
                    max_retries=self.retries,
                )
            if retstart == 0:
                results = response["result"]
            else:
                result = response["result"]
                for key, value in result.items():
                    if key in list(results.keys()):
                        results[key] += value
                    else:
                        results[key] = value
        return results

    def get_efetch_response(self, db, term, usehistory="y"):
        assert db in ["sra", "geo"]

        payload = self.esearch_params[db].copy()
        if isinstance(term, list):
            term = " OR ".join(term)
        payload += [("term", term)]

        request = self._send_retryable_request(
            self.base_url["esearch"], params=OrderedDict(payload)
        )
        esearch_response = request.json()
        if "esummaryresult" in esearch_response:
            if self.verbose:
                print("No result found")
            return
        if "error" in esearch_response:
            # API rate limite exceeded
            esearch_response = _retry_response(
                self.base_url["esearch"],
                payload,
                "esearchresult",
                max_retries=self.retries,
            )

        n_records = int(esearch_response["esearchresult"]["count"])

        results = {}
        for retstart in get_retmax(n_records):
            payload = self.efetch_params.copy()
            payload += self.create_esummary_params(esearch_response["esearchresult"])
            payload = OrderedDict(payload)
            payload["retstart"] = retstart
            request = self._send_retryable_request(
                self.base_url["efetch"], params=OrderedDict(payload)
            )
            request_text = request.text.strip()
            try:
                request_json = request.json()
            except Exception:
                request_json = {}  # eval(request_text)

            if "error" in request_json:
                # print("Encountered: {}".format(request_json))
                # print("Headers: {}".format(request.headers))
                # Handle API-rate limit exceeding
                try:
                    retry_after = request.headers["Retry-After"]
                except KeyError:
                    if request_json["error"] == "error forwarding request":
                        error_msg = "Encountered error while making request.\n"
                        if self.verbose:
                            sys.stderr.write(error_msg)
                        raise RuntimeError(error_msg.strip())
                time.sleep(int(retry_after))
                # try again
                request = self._send_retryable_request(
                    self.base_url["efetch"], params=OrderedDict(payload)
                )
                request_text = request.text.strip()
                try:
                    request_json = request.json()
                    if request_json["error"] == "error forwarding request":
                        if self.verbose:
                            sys.stderr.write(
                                "Encountered error while making request.\n"
                            )

                        return
                except:
                    request_json = {}  # eval(request_text)
            try:
                xml_response = xmltodict.parse(
                    request_text, process_namespaces=False, dict_constructor=OrderedDict
                )

                exp_response = xml_response.get("EXPERIMENT_PACKAGE_SET", {})
                response = exp_response.get("EXPERIMENT_PACKAGE", {})
            except ExpatError as e:
                error_msg = "Unable to parse xml: {}{}".format(request_text, os.linesep)
                if self.verbose:
                    sys.stderr.write(error_msg)

                raise ValueError(error_msg.strip()) from e
            if not response:
                error_msg = "Unable to parse xml response. Received: {}{}".format(
                    xml_response, os.linesep
                )

                if self.verbose:
                    sys.stderr.write(error_msg)

                raise ValueError(error_msg.strip())
            if retstart == 0:
                results = response
            else:
                result = response
                for value in result:
                    results.append(value)
            time.sleep(self.sleep_time)
        return results

    def sra_metadata(
        self,
        srp,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
        output_read_lengths=False,
        include_pmids=False,
        enrich=False,
        enrich_backend="ollama/granite4:3b",
        embedding_model="abhinand/MedEmbed-large-v0.1",
        **kwargs,
    ):
        # NOTE: When enriching, use pysraweb API and flatten like the UI table.
        if enrich:
            if detailed:
                raise ValueError(
                    "detailed is not supported with enrich; enrichment uses "
                    "the pysraweb API output."
                )
            df = self._pysraweb_sra_metadata(srp)
            if df is None or df.empty:
                return df
            from pysradb.enrichment import enrich_df

            return enrich_df(
                df,
                enrichment_backend=enrich_backend,
                embedding_model=embedding_model,
            )

        esummary_result = self.get_esummary_response("sra", srp)
        try:
            uids = esummary_result["uids"]
        except KeyError:
            return None

        exps_xml = OrderedDict()
        runs_xml = OrderedDict()

        exps_json = OrderedDict()
        runs_json = OrderedDict()
        for uid in uids:
            exps_xml[uid] = self.format_xml(esummary_result[uid]["expxml"])
            runs_xml[uid] = self.format_xml(esummary_result[uid]["runs"])

        for uid in uids:
            exps_json[uid] = self.xml_to_json(exps_xml[uid])
            runs_json[uid] = self.xml_to_json(runs_xml[uid])

        sra_record = []
        for uid, run_json in runs_json.items():
            exp_json = exps_json[uid]
            exp_summary = exp_json["Summary"]
            exp_title = exp_summary.get("Title", pd.NA)
            exp_platform = exp_summary.get("Platform", {})
            statistics = exp_summary.get("Statistics", {})
            if isinstance(exp_platform, OrderedDict):
                exp_platform_model = exp_platform.get("@instrument_model", pd.NA)
                exp_platform_desc = exp_platform.get("#text", pd.NA)
            else:
                exp_platform_model = pd.NA
                exp_platform_desc = pd.NA

            exp_total_runs = statistics.get("@total_runs", pd.NA)
            exp_total_spots = statistics.get("@total_spots", pd.NA)
            exp_total_size = statistics.get("@total_size", pd.NA)

            # experiment_accession
            exp_ID = exp_json["Experiment"]["@acc"]
            # experiment_title
            exp_name = exp_json["Experiment"]["@name"]

            exp_organism = exp_json.get("Organism", pd.NA)
            exp_organism_name = pd.NA
            exp_taxid = pd.NA
            if isinstance(exp_organism, dict):
                exp_organism_name = exp_organism.get("@ScientificName", pd.NA)
                exp_taxid = exp_organism["@taxid"]

            exp_instrument = list(exp_json["Instrument"].values())[0]

            exp_sample = exp_json["Sample"]
            # sample_accession
            exp_sample_ID = exp_sample["@acc"]
            # sample_title
            exp_sample_name = exp_sample["@name"]

            exp_library_descriptor = exp_json["Library_descriptor"]
            # library_strategy
            exp_library_strategy = exp_library_descriptor["LIBRARY_STRATEGY"]
            if isinstance(exp_library_strategy, dict):
                exp_library_strategy = exp_library_strategy["#text"]
            # library_source
            exp_library_source = exp_library_descriptor["LIBRARY_SOURCE"]
            if isinstance(exp_library_source, dict):
                exp_library_source = exp_library_source["#text"]
            # library_selection
            exp_library_selection = exp_library_descriptor["LIBRARY_SELECTION"]
            if isinstance(exp_library_selection, dict):
                exp_library_selection = exp_library_selection["#text"]
            # library_name
            exp_library_name = exp_library_descriptor.get("LIBRARY_NAME", "")
            if isinstance(exp_library_selection, dict):
                exp_library_name = exp_library_name["#text"]
            # library_layout
            exp_library_layout = list(exp_library_descriptor["LIBRARY_LAYOUT"].keys())[
                0
            ]
            # biosample
            exp_biosample = exp_json.get("Biosample", pd.NA)
            # bioproject
            exp_bioproject = exp_json.get("Bioproject", pd.NA)

            experiment_record = OrderedDict()
            experiment_record["study_accession"] = exp_json["Study"]["@acc"]
            experiment_record["study_title"] = exp_json["Study"]["@name"]
            experiment_record["experiment_accession"] = exp_ID
            experiment_record["experiment_title"] = exp_name
            experiment_record["experiment_desc"] = exp_title

            experiment_record["organism_taxid"] = exp_taxid
            experiment_record["organism_name"] = exp_organism_name

            experiment_record["library_name"] = exp_library_name
            experiment_record["library_strategy"] = exp_library_strategy
            experiment_record["library_source"] = exp_library_source
            experiment_record["library_selection"] = exp_library_selection
            experiment_record["library_layout"] = exp_library_layout
            experiment_record["sample_accession"] = exp_sample_ID
            experiment_record["sample_title"] = exp_sample_name
            experiment_record["biosample"] = exp_biosample
            experiment_record["bioproject"] = exp_bioproject
            experiment_record["instrument"] = exp_instrument
            experiment_record["instrument_model"] = exp_platform_model
            experiment_record["instrument_model_desc"] = exp_platform_desc
            experiment_record["total_spots"] = exp_total_spots
            experiment_record["total_size"] = exp_total_size
            if not run_json:
                # Sometimes the run_accession is not populated by NCBI:
                # df2 = self.srx_to_srr(exp_ID)
                # extra_fields = set(experiment_record.keys()).difference(df2.columns.tolist())
                # for idx, row in df2.iterrows():
                #    for field in extra_fields:
                #        experiment_record[field] = row[field]
                sra_record.append(experiment_record)
                continue
            runs = run_json["Run"]
            if not isinstance(runs, list):
                runs = [runs]
            for run_record in runs:
                run_accession = run_record["@acc"]
                run_total_spots = run_record["@total_spots"]
                run_total_bases = run_record["@total_bases"]

                experiment_record["run_accession"] = run_accession
                experiment_record["run_total_spots"] = run_total_spots
                experiment_record["run_total_bases"] = run_total_bases

                sra_record.append(experiment_record.copy())

        # TODO: the detailed call below does redundant operations
        # the code above this can be completeley done away with

        # Convert any unhashable types to hashable ones before creating DataFrame
        hashable_records = []
        for record in sra_record:
            hashable_record = {k: _make_hashable(v) for k, v in record.items()}
            hashable_records.append(hashable_record)

        metadata_df = pd.DataFrame(hashable_records).drop_duplicates()
        if "run_accession" in metadata_df.columns:
            metadata_df = metadata_df.sort_values(by="run_accession")
        metadata_df.columns = [x.lower().strip() for x in metadata_df.columns]
        # Filter out XML namespace artifacts and replace with NA
        metadata_df = metadata_df.replace(
            regex=r"^@xmlns.*", value=pd.NA
        ).infer_objects(copy=False)
        basic_cols = metadata_df.columns
        if not detailed:
            return metadata_df

        time.sleep(self.sleep_time)
        efetch_result = self.get_efetch_response("sra", srp)
        if not isinstance(efetch_result, list):
            if efetch_result:
                efetch_result = [efetch_result]
            else:
                return None

        detailed_records = []
        for record in efetch_result:
            if "SAMPLE" in record.keys() and "SAMPLE_ATTRIBUTES" in record["SAMPLE"]:
                sample_attributes = record["SAMPLE"]["SAMPLE_ATTRIBUTES"][
                    "SAMPLE_ATTRIBUTE"
                ]
            else:
                sample_attributes = []
            if isinstance(sample_attributes, OrderedDict):
                sample_attributes = [sample_attributes]
            exp_record = record["EXPERIMENT"]
            exp_attributes = exp_record.get("EXPERIMENT_ATTRIBUTES", {})
            run_sets = record["RUN_SET"].get("RUN", [])

            if not isinstance(run_sets, list):
                run_sets = [run_sets]

            for run_set in run_sets:
                detailed_record = OrderedDict()
                if not run_json:
                    # Add experiment accession if no run info found earlier
                    detailed_record["experiment_accession"] = exp_record["@accession"]
                # detailed_record["experiment_title"] = exp_record["TITLE"]
                for key, values in exp_attributes.items():
                    key = key.lower()
                    for value_x in values:
                        if not isinstance(value_x, dict):
                            continue
                        tag = value_x["TAG"].lower()
                        value = value_x["VALUE"] if "VALUE" in value_x else None
                        detailed_record[tag] = value
                lib_record = exp_record["DESIGN"]["LIBRARY_DESCRIPTOR"]
                for key, value in lib_record.items():
                    key = key.lower()
                    if key == "library_layout":
                        value = list(value.keys())[0]
                    elif key == "library_construction_protocol":
                        continue
                    # detailed_record[key] = value

                detailed_record["run_accession"] = run_set["@accession"]
                detailed_record["run_alias"] = run_set["@alias"]
                sra_files = run_set.get("SRAFiles", {})
                sra_files = sra_files.get("SRAFile", {})
                if isinstance(sra_files, OrderedDict):
                    # detailed_record["sra_url"] = sra_files.get("@url", pd.NA)
                    if "Alternatives" in sra_files.keys():
                        alternatives = sra_files["Alternatives"]
                        if not isinstance(alternatives, list):
                            alternatives = [alternatives]
                        for alternative in alternatives:
                            org = alternative["@org"].lower()
                            for key in alternative.keys():
                                if key == "@org":
                                    continue
                                detailed_record[
                                    "{}_{}".format(org, key.replace("@", ""))
                                ] = alternative[key]

                else:
                    for sra_file in sra_files:
                        # Multiple download URLs
                        # Use the one where the download filename corresponds to the SRR
                        cluster = sra_file.get("@cluster", None).lower().strip()
                        if cluster is None:
                            continue
                        for key in sra_file.keys():
                            if key == "@cluster":
                                continue
                            if key == "Alternatives":
                                # Example: SRP184142
                                alternatives = sra_file["Alternatives"]
                                if not isinstance(alternatives, list):
                                    alternatives = [alternatives]
                                for alternative in alternatives:
                                    org = alternative["@org"].lower()
                                    for key in alternative.keys():
                                        if key == "@org":
                                            continue
                                        detailed_record[
                                            "{}_{}".format(org, key.replace("@", ""))
                                        ] = alternative[key]
                            else:
                                detailed_record[
                                    "{}_{}".format(cluster, key.replace("@", ""))
                                ] = sra_file[key]

                expt_ref = run_set["EXPERIMENT_REF"]
                detailed_record["experiment_alias"] = expt_ref.get("@refname", "")
                # detailed_record["run_total_bases"] = run_set["@total_bases"]
                # detailed_record["run_total_spots"] = run_set["@total_spots"]
                for sample_attribute in sample_attributes:
                    dict_values = list(sample_attribute.values())
                    if len(dict_values) > 1:
                        detailed_record[dict_values[0]] = dict_values[1]
                    else:
                        # TODO: Investigate why these fields have just the key
                        # but no value
                        pass
                detailed_records.append(detailed_record)
        detailed_record_df = pd.DataFrame(detailed_records).drop_duplicates()
        if (
            "run_accession" in metadata_df.keys()
            and "run_accession" in detailed_record_df.keys()
        ):
            metadata_df = metadata_df.merge(
                detailed_record_df, on="run_accession", how="outer"
            )
        elif "experiment_accession" in detailed_record_df.keys():
            metadata_df = metadata_df.merge(
                detailed_record_df, on="experiment_accession", how="outer"
            )

        metadata_df = metadata_df[metadata_df.columns.dropna()]
        metadata_df = metadata_df.drop_duplicates()
        metadata_df = metadata_df.replace(r"^\s*$", pd.NA, regex=True)
        ena_cols = [
            "ena_fastq_http",
            "ena_fastq_http_1",
            "ena_fastq_http_2",
            "ena_fastq_ftp",
            "ena_fastq_ftp_1",
            "ena_fastq_ftp_2",
        ]
        empty_df = pd.DataFrame(columns=ena_cols)
        metadata_df = pd.concat((metadata_df, empty_df), axis=0)

        if "run_accession" in metadata_df.columns:
            metadata_df = metadata_df.set_index("run_accession")
        # multithreading lookup on ENA, since a lot of time is spent waiting
        # for its reply
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # load our function calls into a list of futures
            futures = [
                executor.submit(self.fetch_ena_fastq, srp)
                for srp in metadata_df.study_accession.unique()
            ]
            # now proceed synchronously
            for future in concurrent.futures.as_completed(futures):
                ena_results = future.result()
                if ena_results.shape[0]:
                    ena_results = ena_results.set_index("run_accession")
                    metadata_df.update(ena_results)
        metadata_df = metadata_df.reset_index()
        metadata_df = metadata_df.fillna(pd.NA)
        metadata_df.columns = [x.lower().strip() for x in metadata_df.columns]

        # Add PMID column when detailed=True and include_pmids=True
        # Not fetching pmids when user asks for enriched output
        if include_pmids:
            try:
                sra_accessions = [srp] if isinstance(srp, str) else srp
                pmid_df = self.sra_to_pmid(sra_accessions)

                if pmid_df is not None and not pmid_df.empty:
                    pmid_map = {}
                    for _, row in pmid_df.iterrows():
                        study_acc = row.get("sra_accession", None)
                        pmid = row.get("pmid")
                        if not pd.isna(pmid):
                            if study_acc not in pmid_map:
                                pmid_map[study_acc] = []
                            pmid_map[study_acc].append(str(pmid))

                    metadata_df["pmid"] = metadata_df.apply(
                        lambda row: ",".join(
                            pmid_map.get(row.get("study_accession", ""), [""])
                        ),
                        axis=1,
                    )
                    metadata_df["pmid"] = metadata_df["pmid"].replace("", pd.NA)
                else:
                    metadata_df["pmid"] = pd.NA

            except Exception as e:
                metadata_df["pmid"] = pd.NA

        # Filter out XML namespace artifacts and replace with NA
        metadata_df = metadata_df.replace(
            regex=r"^@xmlns.*", value=pd.NA
        ).infer_objects(copy=False)

        # Add GSE and GSM columns when detailed=True
        if detailed:
            try:
                unique_srps = metadata_df["study_accession"].dropna().unique().tolist()
                if unique_srps:
                    gse_df = self.srp_to_gse(unique_srps)
                    if gse_df is not None and not gse_df.empty:
                        srp_to_gse_map = {}
                        for _, row in gse_df.iterrows():
                            srp_acc = row.get("study_accession")
                            gse_acc = row.get("study_alias")
                            if not pd.isna(srp_acc) and not pd.isna(gse_acc):
                                if srp_acc not in srp_to_gse_map:
                                    srp_to_gse_map[srp_acc] = []
                                srp_to_gse_map[srp_acc].append(gse_acc)

                        metadata_df["study_geo_accession"] = metadata_df[
                            "study_accession"
                        ].map(
                            lambda x: (
                                ",".join(srp_to_gse_map.get(x, []))
                                if x in srp_to_gse_map
                                else pd.NA
                            )
                        )
                        metadata_df["study_geo_accession"] = metadata_df[
                            "study_geo_accession"
                        ].replace("", pd.NA)
                    else:
                        metadata_df["study_geo_accession"] = pd.NA
                else:
                    metadata_df["study_geo_accession"] = pd.NA

                unique_srxs = (
                    metadata_df["experiment_accession"].dropna().unique().tolist()
                )
                if unique_srxs:
                    gsm_response = self.fetch_gds_results(unique_srxs)
                    if gsm_response is not None and not gsm_response.empty:
                        srx_to_gsm_map = {}
                        for _, row in gsm_response.iterrows():
                            if row.get("entrytype") == "GSM":
                                gsm_acc = row.get("accession")
                                srx_acc = row.get("SRA")
                                if not pd.isna(srx_acc) and not pd.isna(gsm_acc):
                                    srx_to_gsm_map[srx_acc] = gsm_acc

                        metadata_df["experiment_geo_accession"] = metadata_df[
                            "experiment_accession"
                        ].map(lambda x: srx_to_gsm_map.get(x, pd.NA))
                    else:
                        metadata_df["experiment_geo_accession"] = pd.NA
                else:
                    metadata_df["experiment_geo_accession"] = pd.NA

            except Exception as e:
                metadata_df["study_geo_accession"] = pd.NA
                metadata_df["experiment_geo_accession"] = pd.NA

        if enrich and not metadata_df.empty:
            from pysradb.enrichment import enrich_df

            metadata_df = enrich_df(metadata_df, list(basic_cols), enrich_backend)

        if "run_accession" in metadata_df.columns:
            return metadata_df.sort_values(by="run_accession")
        return metadata_df

    def fetch_gds_results(self, gse, **kwargs):
        result = self.get_esummary_response("geo", gse)

        try:
            uids = result["uids"]
        except KeyError:
            if self.verbose:
                print(
                    "No results found for {} | Obtained result: {}".format(gse, result)
                )
            return None
        gse_records = []
        for uid in uids:
            record = result[uid]
            del record["uid"]
            extrelations = record.get("extrelations") or []
            if extrelations:
                for extrelation in extrelations:
                    keys = list(extrelation.keys())
                    values = list(extrelation.values())
                    assert sorted(keys) == sorted(
                        ["relationtype", "targetobject", "targetftplink"]
                    )
                    assert len(values) == 3
                    record[extrelation["relationtype"]] = extrelation["targetobject"]
                del record["extrelations"]
                gse_records.append(record)
                continue

            # Fallback for records without extrelations (e.g., spatial transcriptomics datasets)
            samples = record.get("samples") or []
            if samples:
                record["samples"] = samples
            gse_records.append(record)
        if not len(gse_records):
            if self.verbose:
                print("No results found for {}".format(gse))
            return None
        return pd.DataFrame(gse_records)

    def fetch_gsm_soft(self, gsm_ids):
        """
        Fetch detailed GSM metadata in SOFT format.

        Args:
            gsm_ids: List of GSM accessions

        Returns:
            Dictionary mapping GSM accession to parsed SOFT metadata
        """
        if isinstance(gsm_ids, str):
            gsm_ids = [gsm_ids]

        gsm_data = {}
        for gsm in gsm_ids:
            try:
                url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gsm}&targ=self&form=text&view=full"
                response = self._send_retryable_request(url)
                response.raise_for_status()

                # Parse SOFT format
                soft_text = response.text
                metadata = {}
                characteristics = []

                for line in soft_text.split("\n"):
                    line = line.strip()
                    if line.startswith("!Sample_"):
                        if " = " in line:
                            key, value = line.split(" = ", 1)
                            key = key.replace("!Sample_", "").lower()

                            # Handle characteristics specially - they can appear multiple times
                            if "characteristics" in key:
                                characteristics.append(value)
                            else:
                                # Store in metadata dict
                                # Join multiple values with semicolon for consistency
                                if key not in metadata:
                                    metadata[key] = value
                                elif isinstance(metadata[key], list):
                                    metadata[key].append(value)
                                else:
                                    # Convert to list if we have multiple values
                                    metadata[key] = [metadata[key], value]

                # Convert list values to semicolon-separated strings
                for key, value in metadata.items():
                    if isinstance(value, list):
                        metadata[key] = "; ".join(str(v) for v in value)

                # Process characteristics into a dict
                char_dict = {}
                for char in characteristics:
                    if ": " in char:
                        char_key, char_val = char.split(": ", 1)
                        char_dict[char_key.strip().lower()] = char_val.strip()

                metadata["characteristics"] = char_dict
                gsm_data[gsm] = metadata

            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not fetch SOFT data for {gsm}: {e}")
                gsm_data[gsm] = {}

        return gsm_data

    def geo_metadata(
        self,
        gse,
        sample_attribute=False,
        detailed=False,
        expand_sample_attributes=False,
        include_pmids=False,
        enrich=False,
        enrich_backend="ollama/granite4:3b",
        embedding_model="abhinand/MedEmbed-large-v0.1",
        **kwargs,
    ):
        if enrich:
            if detailed:
                raise ValueError(
                    "detailed is not supported with enrich; enrichment uses "
                    "the pysraweb API output."
                )
            df = self._pysraweb_geo_metadata(gse)
            if df is None or df.empty:
                return df
            from pysradb.enrichment import enrich_df

            return enrich_df(
                df,
                enrichment_backend=enrich_backend,
                embedding_model=embedding_model,
            )

        if isinstance(gse, str):
            gse = [gse]
        if not gse:
            return pd.DataFrame(
                columns=[
                    "study_accession",
                    "study_title",
                    "study_summary",
                    "organism_name",
                    "platform_accession",
                    "platform_title",
                    "experiment_type",
                    "bioproject",
                    "submission_date",
                    "supplementary_files",
                    "series_ftp",
                    "sample_accession",
                    "sample_title",
                ]
            )

        geo_response = self.get_esummary_response("geo", gse)
        if not geo_response:
            return pd.DataFrame(
                columns=[
                    "study_accession",
                    "study_title",
                    "study_summary",
                    "organism_name",
                    "platform_accession",
                    "platform_title",
                    "experiment_type",
                    "bioproject",
                    "submission_date",
                    "supplementary_files",
                    "series_ftp",
                    "sample_accession",
                    "sample_title",
                ]
            )

        gse_records = []
        sample_accessions = []
        for uid in geo_response.get("uids", []):
            record = geo_response.get(uid, {})
            if record.get("entrytype") != "GSE":
                continue
            gse_records.append(record)
            for sample in record.get("samples") or []:
                accession = sample.get("accession")
                if accession and accession not in sample_accessions:
                    sample_accessions.append(accession)

        sample_details = {}
        gsm_soft_data = {}
        if (sample_attribute or detailed) and sample_accessions:
            sample_response = self.get_esummary_response("geo", sample_accessions)
            if sample_response:
                for uid in sample_response.get("uids", []):
                    entry = sample_response.get(uid, {})
                    if entry.get("entrytype") == "GSM":
                        sample_details[entry.get("accession")] = entry

            # Fetch full SOFT metadata when detailed=True
            if detailed:
                gsm_soft_data = self.fetch_gsm_soft(sample_accessions)

        # Get SRP mappings for all GSE IDs using gse_to_srp
        gse_to_srp_map = {}
        if gse and detailed:
            try:
                srp_df = self.gse_to_srp(gse)
                if not srp_df.empty:
                    # Group by study_alias and join multiple SRPs with comma
                    for gse_id in gse:
                        srps = (
                            srp_df[srp_df["study_alias"] == gse_id]["study_accession"]
                            .dropna()
                            .tolist()
                        )
                        if srps:
                            gse_to_srp_map[gse_id] = ",".join(srps)
            except Exception:
                pass

        # Get SRX mappings for all GSM samples
        gsm_to_srx_map = {}
        if sample_accessions and detailed:
            try:
                # Use fetch_gds_results to get SRX from GSM entries
                gsm_response = self.fetch_gds_results(sample_accessions)
                if gsm_response is not None and not gsm_response.empty:
                    for _, row in gsm_response.iterrows():
                        if row.get("entrytype") == "GSM":
                            gsm_acc = row.get("accession")
                            srx = row.get("SRA")
                            if gsm_acc and srx and not pd.isna(srx):
                                gsm_to_srx_map[gsm_acc] = srx
            except Exception:
                pass

        rows = []
        for record in gse_records:
            study_accession = record.get("accession", pd.NA)
            platform = record.get("gpl", pd.NA)
            if (
                isinstance(platform, str)
                and platform.strip()
                and not platform.upper().startswith("GPL")
                and platform.replace(" ", "").isdigit()
            ):
                platform_accession = f"GPL{platform.strip()}"
            else:
                platform_accession = platform if platform else pd.NA

            base_row = OrderedDict(
                [
                    ("study_accession", study_accession),
                    ("study_title", record.get("title", pd.NA)),
                    ("study_summary", record.get("summary", pd.NA)),
                    ("organism_name", record.get("taxon", pd.NA)),
                    ("platform_accession", platform_accession),
                    ("platform_title", record.get("platformtitle", pd.NA)),
                    ("experiment_type", record.get("gdstype", pd.NA)),
                    ("bioproject", record.get("bioproject", pd.NA)),
                    ("submission_date", record.get("pdat", pd.NA)),
                    ("supplementary_files", record.get("suppfile", pd.NA)),
                    ("series_ftp", record.get("ftplink", pd.NA)),
                    ("sample_accession", pd.NA),
                    ("sample_title", pd.NA),
                ]
            )

            # Add SRP column when detailed=True
            if detailed:
                base_row["study_sra_accession"] = gse_to_srp_map.get(
                    study_accession, pd.NA
                )

            if sample_attribute:
                base_row["sample_summary"] = pd.NA
            if detailed:
                base_row["sample_ftp"] = pd.NA
                base_row["sample_supplementary"] = pd.NA
                base_row["sample_geo2r"] = pd.NA
                base_row["experiment_sra_accession"] = pd.NA
                # Add SOFT metadata fields
                base_row["sample_type"] = pd.NA
                base_row["sample_source_name"] = pd.NA
                base_row["sex"] = pd.NA
                base_row["age"] = pd.NA
                base_row["tissue"] = pd.NA
                base_row["cell_type"] = pd.NA
                base_row["disease"] = pd.NA
                base_row["treatment"] = pd.NA
                base_row["extract_protocol"] = pd.NA
                base_row["label_protocol"] = pd.NA

            samples = record.get("samples") or []
            if samples:
                for sample in samples:
                    row = base_row.copy()
                    sample_acc = sample.get("accession", pd.NA)
                    row["sample_accession"] = sample_acc
                    row["sample_title"] = sample.get("title", pd.NA)
                    sample_entry = sample_details.get(sample_acc, {})
                    if sample_attribute:
                        row["sample_summary"] = sample_entry.get("summary", pd.NA)
                    if detailed:
                        row["sample_ftp"] = sample_entry.get("ftplink", pd.NA)
                        row["sample_supplementary"] = sample_entry.get(
                            "suppfile", pd.NA
                        )
                        row["sample_geo2r"] = sample_entry.get("geo2r", pd.NA)
                        # Add SRX from gsm_to_srx_map
                        row["experiment_sra_accession"] = gsm_to_srx_map.get(
                            sample_acc, pd.NA
                        )

                        # Add SOFT metadata - extract ALL available fields
                        soft_data = gsm_soft_data.get(sample_acc, {})
                        if soft_data:
                            # Add all SOFT fields with sample_ prefix (characteristics handled separately)
                            for soft_key, soft_val in soft_data.items():
                                if soft_key != "characteristics":
                                    col_name = f"sample_{soft_key}"
                                    row[col_name] = soft_val

                            # Also extract commonly used fields to canonical column names for convenience
                            row["sample_type"] = soft_data.get("type_ch1", pd.NA)
                            row["sample_source_name"] = soft_data.get(
                                "source_name_ch1", pd.NA
                            )
                            row["extract_protocol"] = soft_data.get(
                                "extract_protocol_ch1", pd.NA
                            )
                            row["label_protocol"] = soft_data.get(
                                "label_protocol_ch1", pd.NA
                            )

                            # Process characteristics: add standard ones to canonical names, preserve all as-is
                            chars = soft_data.get("characteristics", {})

                            # Standard fields with canonical names (for backward compatibility)
                            row["sex"] = chars.get("sex", chars.get("gender", pd.NA))
                            row["age"] = chars.get("age", pd.NA)
                            row["tissue"] = chars.get(
                                "tissue",
                                chars.get(
                                    "tissue type",
                                    chars.get("structures", chars.get("organ", pd.NA)),
                                ),
                            )
                            row["cell_type"] = chars.get(
                                "cell type",
                                chars.get("cell_type", chars.get("celltype", pd.NA)),
                            )
                            row["disease"] = chars.get(
                                "disease",
                                chars.get(
                                    "disease state",
                                    chars.get(
                                        "disease_state",
                                        chars.get("disease_status", pd.NA),
                                    ),
                                ),
                            )
                            row["treatment"] = chars.get(
                                "treatment",
                                chars.get("compound", chars.get("drug", pd.NA)),
                            )

                            # Add ALL characteristics as-is (including custom ones)
                            for char_key, char_val in chars.items():
                                row[char_key] = char_val

                    rows.append(row)
            else:
                rows.append(base_row)

        if not rows:
            return pd.DataFrame(
                columns=list(base_row.keys()) if "base_row" in locals() else None
            )

        metadata_df = pd.DataFrame(rows)

        if include_pmids:
            try:
                pmid_df = self.gse_to_pmid(gse)
            except Exception:
                pmid_df = None
            if pmid_df is not None and not pmid_df.empty:
                pmid_map = {}
                for _, row in pmid_df.iterrows():
                    gse_acc = row.get("gse_accession")
                    pmid = row.get("pmid")
                    if pd.isna(pmid):
                        continue
                    pmid_map.setdefault(gse_acc, []).append(str(pmid))

                metadata_df["pmid"] = metadata_df["study_accession"].map(
                    lambda accession: (
                        ",".join(pmid_map.get(accession, []))
                        if accession in pmid_map
                        else pd.NA
                    )
                )
            else:
                metadata_df["pmid"] = pd.NA

        metadata_df = metadata_df.replace("", pd.NA)
        if "sample_accession" in metadata_df.columns:
            metadata_df = metadata_df.sort_values(
                by=["study_accession", "sample_accession"],
                na_position="last",
            )
        metadata_df = metadata_df.reset_index(drop=True)

        if detailed and not metadata_df.empty:
            try:
                gse_bioproject_map = {}
                for _, row in metadata_df.iterrows():
                    gse_id = row.get("study_accession")
                    bioproject = row.get("bioproject")
                    if gse_id and str(gse_id).startswith("GSE"):
                        if bioproject and str(bioproject).startswith("PRJNA"):
                            gse_bioproject_map[gse_id] = bioproject

                gse_srp_map = {}
                all_fastq_data = []

                for gse_id, bioproject in gse_bioproject_map.items():
                    try:
                        srp_list = self.bioproject_to_srp(bioproject)
                        if srp_list:
                            srp = srp_list[0]  # Use the first SRP found
                            gse_srp_map[gse_id] = srp

                            # Fetch SRA metadata and fastq URLs for this SRP
                            try:
                                sra_metadata_df = self.sra_metadata(srp)
                                if not sra_metadata_df.empty:
                                    fastq_df = self.fetch_ena_fastq(srp)
                                    if not fastq_df.empty:
                                        merged_df = sra_metadata_df.merge(
                                            fastq_df, on="run_accession", how="left"
                                        )
                                        merged_df["gse_from_bioproject"] = gse_id
                                        merged_df["srp_from_bioproject"] = srp
                                        all_fastq_data.append(merged_df)
                                time.sleep(self.sleep_time)
                            except Exception:
                                pass
                    except Exception:
                        pass

                # If we found fastq data, merge it with the main metadata via GSM->SRX->SRR mapping
                if all_fastq_data and sample_accessions:
                    try:
                        # Combine all fastq data
                        combined_fastq = pd.concat(all_fastq_data, ignore_index=True)

                        # Map GSM to SRX for matching
                        gsm_to_srx_map = {}
                        for gsm_id in sample_accessions:
                            try:
                                srx_df = self.gsm_to_srx(gsm_id)
                                if (
                                    not srx_df.empty
                                    and "experiment_accession" in srx_df.columns
                                ):
                                    srx_list = (
                                        srx_df["experiment_accession"].dropna().tolist()
                                    )
                                    if srx_list:
                                        gsm_to_srx_map[gsm_id] = srx_list[0]
                                time.sleep(0.1)
                            except Exception:
                                pass

                        # Add fastq columns to metadata_df
                        fastq_cols = [
                            col
                            for col in combined_fastq.columns
                            if "fastq" in col.lower() or "ftp" in col.lower()
                        ]
                        for col in fastq_cols:
                            if col not in metadata_df.columns:
                                metadata_df[col] = pd.NA

                        # Create a mapping from SRX->run_accession->fastq URLs
                        srx_to_fastq_map = {}
                        for _, row in combined_fastq.iterrows():
                            srx = row.get("experiment_accession", pd.NA)
                            run_acc = row.get("run_accession", pd.NA)
                            if not pd.isna(srx) and not pd.isna(run_acc):
                                if srx not in srx_to_fastq_map:
                                    srx_to_fastq_map[srx] = {}
                                srx_to_fastq_map[srx][run_acc] = row

                        # Merge fastq URLs based on GSM->SRX->fastq mapping
                        for col in fastq_cols:

                            def get_fastq_url(row):
                                gsm = row.get("sample_accession", pd.NA)
                                if pd.isna(gsm):
                                    return pd.NA
                                # Get SRX for this GSM
                                srx = gsm_to_srx_map.get(gsm, pd.NA)
                                if pd.isna(srx) or srx not in srx_to_fastq_map:
                                    return pd.NA
                                # Get first run accession for this SRX
                                run_accs = list(srx_to_fastq_map[srx].keys())
                                if run_accs:
                                    fastq_row = srx_to_fastq_map[srx][run_accs[0]]
                                    return fastq_row.get(col, pd.NA)
                                return pd.NA

                            metadata_df[col] = metadata_df.apply(get_fastq_url, axis=1)
                    except Exception:
                        pass
            except Exception:
                pass

        # Enrich metadata if requested
        if enrich and not metadata_df.empty:
            from pysradb.enrichment import enrich_df

            metadata_df = enrich_df(metadata_df, enrichment_backend=enrich_backend)

        return metadata_df

    def _pysraweb_get_json(self, path, params=None, timeout=30):
        url = f"{self.pysraweb_api_url.rstrip('/')}/{path.lstrip('/')}"
        response = self._send_retryable_request(url, params=params)
        response.raise_for_status()
        return response.json()

    def _pysraweb_fetch_samples(self, accessions):
        if not accessions:
            return {}
        unique_accessions = [acc for acc in dict.fromkeys(accessions) if acc]
        samples = {}

        def fetch_one(acc):
            try:
                return acc, self._pysraweb_get_json(f"sample/{acc}")
            except Exception:
                return acc, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_one, acc) for acc in unique_accessions]
            for future in concurrent.futures.as_completed(futures):
                acc, data = future.result()
                if data:
                    samples[acc] = data
        return samples

    def _pysraweb_sra_metadata(self, srp):
        if isinstance(srp, str):
            srp_list = [srp]
        else:
            srp_list = srp or []

        all_rows = []
        attribute_keys = set()

        for accession in srp_list:
            try:
                experiments = self._pysraweb_get_json(
                    f"project/{accession}/experiments"
                )
            except Exception:
                continue

            if not experiments:
                continue

            sample_accessions = []
            for exp in experiments:
                if (
                    exp
                    and isinstance(exp.get("samples"), list)
                    and len(exp.get("samples")) > 0
                ):
                    sample_accessions.append(exp["samples"][0])
            samples_map = self._pysraweb_fetch_samples(sample_accessions)

            parsed_attributes = {}
            for sample_acc, sample in samples_map.items():
                attrs = sample.get("attributes_json")
                if isinstance(attrs, str):
                    try:
                        attrs = json.loads(attrs)
                    except Exception:
                        attrs = None
                if isinstance(attrs, dict):
                    parsed_attributes[sample_acc] = attrs
                    attribute_keys.update(attrs.keys())
                else:
                    parsed_attributes[sample_acc] = None

            for exp in experiments:
                if not exp:
                    continue
                if not isinstance(exp.get("samples"), list) or not exp.get("samples"):
                    # Match flatten contract: skip experiments with no sample.
                    continue

                sample_acc = exp["samples"][0]
                sample = samples_map.get(sample_acc) if sample_acc else None

                row = OrderedDict(
                    [
                        ("Accession", exp.get("accession", pd.NA)),
                        ("Title", exp.get("title", pd.NA)),
                        (
                            "Library",
                            exp.get("library_name")
                            or exp.get("library_strategy")
                            or pd.NA,
                        ),
                        ("Layout", exp.get("library_layout", pd.NA)),
                        ("Platform", exp.get("platform", pd.NA)),
                        ("Instrument", exp.get("instrument_model", pd.NA)),
                        ("Sample", sample_acc or pd.NA),
                        (
                            "Sample Alias",
                            sample.get("alias", pd.NA) if sample else pd.NA,
                        ),
                        (
                            "Sample Title",
                            sample.get("title", pd.NA) if sample else pd.NA,
                        ),
                        (
                            "Description",
                            sample.get("description", pd.NA) if sample else pd.NA,
                        ),
                        (
                            "Scientific Name",
                            sample.get("scientific_name", pd.NA) if sample else pd.NA,
                        ),
                        (
                            "Taxon ID",
                            sample.get("taxon_id", pd.NA) if sample else pd.NA,
                        ),
                    ]
                )
                row["_attributes_json"] = parsed_attributes.get(sample_acc)
                all_rows.append(row)

        if not all_rows:
            return pd.DataFrame()

        sorted_attribute_keys = sorted(
            [key for key in attribute_keys if key is not None]
        )
        normalized_rows = []
        for row in all_rows:
            normalized = OrderedDict(row)
            attrs = normalized.pop("_attributes_json", None)
            for key in sorted_attribute_keys:
                if isinstance(attrs, dict):
                    normalized[key] = attrs.get(key, pd.NA)
                else:
                    normalized[key] = pd.NA
            normalized_rows.append(normalized)

        df = pd.DataFrame(normalized_rows)
        ordered_columns = [
            "Accession",
            "Title",
            "Library",
            "Layout",
            "Platform",
            "Instrument",
            "Sample",
            "Sample Alias",
            "Sample Title",
            "Description",
            "Scientific Name",
            "Taxon ID",
        ] + sorted_attribute_keys
        for col in ordered_columns:
            if col not in df.columns:
                df[col] = pd.NA
        df = df.loc[:, ordered_columns]
        return df.replace("", pd.NA)

    def _pysraweb_geo_metadata(self, gse):
        if isinstance(gse, str):
            gse_list = [gse]
        else:
            gse_list = gse or []

        all_rows = []
        all_samples = []
        characteristic_tags = set()

        for accession in gse_list:
            try:
                samples = self._pysraweb_get_json(f"geo/series/{accession}/samples")
            except Exception:
                continue

            if not samples:
                continue
            all_samples.extend(samples)

        for sample in all_samples:
            channels = sample.get("channels") or []
            for channel in channels:
                characteristics = channel.get("Characteristics")
                if isinstance(characteristics, list):
                    for char in characteristics:
                        if isinstance(char, dict):
                            tag = char.get("@tag")
                            if tag is not None:
                                characteristic_tags.add(tag)
                elif isinstance(characteristics, dict):
                    tag = characteristics.get("@tag")
                    if tag is not None:
                        characteristic_tags.add(tag)

        sorted_characteristic_tags = sorted(characteristic_tags)

        for sample in all_samples:
            channels = sample.get("channels") or [None]
            for idx, channel in enumerate(channels):
                char_map = {}
                if channel:
                    characteristics = channel.get("Characteristics")
                    if isinstance(characteristics, list):
                        for char in characteristics:
                            if isinstance(char, dict):
                                char_map[char.get("@tag")] = char.get("#text")
                    elif isinstance(characteristics, dict):
                        char_map[characteristics.get("@tag")] = characteristics.get(
                            "#text"
                        )

                organism_value = pd.NA
                if channel:
                    organism = channel.get("Organism")
                    if isinstance(organism, dict):
                        organism_value = organism.get("#text", pd.NA)
                    elif isinstance(organism, list):
                        first_organism = organism[0] if organism else None
                        if isinstance(first_organism, dict):
                            organism_value = first_organism.get("#text", pd.NA)
                        elif first_organism is not None:
                            organism_value = first_organism
                    elif organism is not None:
                        organism_value = organism

                row = OrderedDict(
                    [
                        ("Sample", sample.get("accession", pd.NA)),
                        ("Title", sample.get("title", pd.NA)),
                        ("Description", sample.get("description", pd.NA)),
                        ("Channel Count", sample.get("channel_count", pd.NA)),
                        ("Sample Type", sample.get("sample_type", pd.NA)),
                        ("Platform", sample.get("platform_ref", pd.NA)),
                        (
                            "Channel Position",
                            channel.get("@position") if channel else idx + 1,
                        ),
                        ("Label", channel.get("Label", pd.NA) if channel else pd.NA),
                        ("Source", channel.get("Source", pd.NA) if channel else pd.NA),
                        (
                            "Molecule",
                            channel.get("Molecule", pd.NA) if channel else pd.NA,
                        ),
                        ("Organism", organism_value),
                        (
                            "Label Protocol",
                            channel.get("Label-Protocol", pd.NA) if channel else pd.NA,
                        ),
                        (
                            "Extract Protocol",
                            (
                                channel.get("Extract-Protocol", pd.NA)
                                if channel
                                else pd.NA
                            ),
                        ),
                        (
                            "Hybridization Protocol",
                            sample.get("hybridization_protocol", pd.NA),
                        ),
                        ("Scan Protocol", sample.get("scan_protocol", pd.NA)),
                    ]
                )
                for tag in sorted_characteristic_tags:
                    row[tag] = char_map.get(tag, pd.NA)
                all_rows.append(row)

        if not all_rows:
            return pd.DataFrame()

        df = pd.DataFrame(all_rows)
        ordered_columns = [
            "Sample",
            "Title",
            "Description",
            "Channel Count",
            "Sample Type",
            "Platform",
            "Channel Position",
            "Label",
            "Source",
            "Molecule",
            "Organism",
            "Label Protocol",
            "Extract Protocol",
            "Hybridization Protocol",
            "Scan Protocol",
        ] + sorted_characteristic_tags
        for col in ordered_columns:
            if col not in df.columns:
                df[col] = pd.NA
        df = df.loc[:, ordered_columns]
        return df.replace("", pd.NA)

    def metadata(self, accession, **kwargs):
        """
        Unified method to fetch metadata for SRA or GEO accessions.

        Automatically detects accession type and calls appropriate method.

        Parameters
        ----------
        accession : str or list
            ``SRP``/``GSE`` accession(s).
        **kwargs
            Additional parameters passed to ``sra_metadata()`` or
            ``geo_metadata()``. Examples include ``detailed``, ``enrich``,
            ``enrich_backend``, and ``sample_attribute``.

        Returns
        -------
        pandas.DataFrame
            Metadata table, enriched if ``enrich=True``.

        Examples
        --------
            >>> client = SRAweb()
            >>> df = client.metadata("GSE286254", detailed=True, enrich=True)
            >>> df = client.metadata("SRP253951", detailed=True, enrich=True)
            >>> df = client.metadata(["GSE286254", "GSE147507"], enrich=True)
        """
        if isinstance(accession, str):
            accessions = [accession]
        else:
            accessions = accession

        if not accessions:
            return pd.DataFrame()

        # Detect accession type from first accession
        first_acc = accessions[0].upper()

        if first_acc.startswith("GSE"):
            return self.geo_metadata(accession, **kwargs)
        elif first_acc.startswith("SRP"):
            return self.sra_metadata(accession, **kwargs)
        else:
            raise ValueError(
                f"Unsupported accession type: {first_acc}. "
                "Supported types: GSE (GEO Series), SRP (SRA Project)"
            )

    def download(
        self,
        df,
        out_dir=None,
        filter_by_srx=None,
        skip_confirmation=False,
        use_ascp=False,
        url_col="public_url",
        threads=1,
    ):
        """Download files described by a detailed SRA metadata table.

        Parameters
        ----------
        df : pandas.DataFrame
            Detailed metadata with run accessions and download URL columns.
        out_dir : str, optional
            Root output directory. Defaults to ``pysradb_downloads`` in the
            current working directory.
        filter_by_srx : list, optional
            Experiment accessions to keep before downloading.
        skip_confirmation : bool
            If ``True``, start downloads without prompting.
        use_ascp : bool
            Reserved for compatibility. Aspera downloads are no longer handled
            by this method.
        url_col : str
            Preferred URL column. Falls back to common detailed metadata URL
            columns when the requested column is unavailable.
        threads : int
            Number of concurrent download workers.
        """
        if use_ascp:
            raise NotImplementedError("Aspera downloads are not supported.")
        if df is None or df.empty:
            return pd.DataFrame()
        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "pysradb_downloads")
        if filter_by_srx:
            df = df[df["experiment_accession"].isin(filter_by_srx)]
        if df.empty:
            return pd.DataFrame()

        url_candidates = [
            url_col,
            "download_url",
            "public_url",
            "ena_fastq_http",
            "sra_url",
        ]
        available_url_cols = [col for col in url_candidates if col in df.columns]
        if not available_url_cols:
            raise ValueError(
                "No supported download URL column found. Expected one of: "
                + ", ".join(dict.fromkeys(url_candidates))
            )

        download_df = df.copy()
        download_df["download_url"] = pd.NA
        for candidate in available_url_cols:
            values = download_df[candidate]
            download_df["download_url"] = download_df["download_url"].where(
                download_df["download_url"].notna(), values
            )
        download_df = download_df[download_df["download_url"].notna()].copy()
        if download_df.empty:
            return download_df

        def _row_path(row):
            parts = [
                out_dir,
                str(row.get("study_accession", "unknown_study")),
                str(row.get("experiment_accession", "unknown_experiment")),
            ]
            file_name = os.path.basename(str(row.download_url).split("?")[0])
            if not file_name:
                file_name = str(row.get("run_accession", "download"))
            return os.path.join(*parts, file_name)

        download_df["out_dir"] = download_df.apply(_row_path, axis=1)
        try:
            download_df["filesize"] = download_df.apply(
                lambda row: get_file_size(row, url_col), axis=1
            )
        except Exception:
            download_df["filesize"] = pd.NA

        if not skip_confirmation and not confirm(
            "The following files will be downloaded:\n{}".format(
                download_df[
                    [
                        col
                        for col in [
                            "run_accession",
                            "study_accession",
                            "experiment_accession",
                            "download_url",
                            "out_dir",
                            "filesize",
                        ]
                        if col in download_df.columns
                    ]
                ].to_string(index=False)
            )
        ):
            return download_df

        def _download_row(row):
            os.makedirs(os.path.dirname(row.out_dir), exist_ok=True)
            download_file(row.download_url, row.out_dir, show_progress=True)

        max_workers = max(1, int(threads or 1))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(
                executor.map(_download_row, [row for _, row in download_df.iterrows()])
            )
        return download_df

    def gse_to_gsm(self, gse, **kwargs):
        if isinstance(gse, str):
            gse = [gse]
        gse_df = self.fetch_gds_results(gse, **kwargs)
        gse_df = gse_df.rename(
            columns={
                "accession": "experiment_alias",
                "SRA": "experiment_accession",
                "title": "experiment_title",
                "summary": "sample_attribute",
            }
        )
        # TODO: Fix for multiple GSEs?
        gse_df["study_alias"] = ""
        if len(gse) == 1:
            study_alias = gse[0]
        for index, row in gse_df.iterrows():
            if row.entrytype == "GSE":
                study_alias = row["experiment_accession"]
            # If GSM is ecnountered, apply it the
            # previously encountered GSE
            elif row.entrytype == "GSM":
                gse_df.loc[index, "study_alias"] = study_alias
        gse_df = gse_df[gse_df.entrytype == "GSM"]
        if kwargs and kwargs["detailed"] == True:
            return gse_df
        return gse_df[
            ["study_alias", "experiment_alias", "experiment_accession"]
        ].drop_duplicates()

    def gse_to_srp(self, gse, **kwargs):
        if isinstance(gse, str):
            gse = [gse]
        if not gse:  # Handle empty input
            return pd.DataFrame(columns=["study_alias", "study_accession"])

        gse_df = self.fetch_gds_results(gse, **kwargs)
        if gse_df is None or gse_df.empty:  # Handle case where no results found
            return pd.DataFrame(columns=["study_alias", "study_accession"])

        gse_df = gse_df.rename(
            columns={"accession": "study_alias", "SRA": "study_accession"}
        )
        gse_df_subset = None
        if "GSE" in gse_df.entrytype.unique():
            gse_df_subset = gse_df[gse_df.entrytype == "GSE"]
            common_gses = set(gse_df.study_alias.unique()).intersection(gse)
            if len(common_gses) < len(gse):
                gse_df_subset = None
            # If any GSE entries have no direct SRA accession, fall back to GSM/SRX.
            elif gse_df_subset["study_accession"].isna().any():
                gse_df_subset = None
        if gse_df_subset is None:
            # sometimes SRX ids are returned instead of an entire project
            # see https://github.com/saketkc/pysradb/issues/186
            # GSE: GSE209835; SRP =SRP388275
            gse_df_subset_gse = gse_df[gse_df.entrytype == "GSE"]
            # Include GSEs that are missing OR have NaN study_accessions
            gses_without_srp = gse_df_subset_gse[
                gse_df_subset_gse.study_accession.isna()
            ].study_alias.tolist()
            gse_of_interest = (
                list(set(gse).difference(gse_df.study_alias.unique()))
                + gses_without_srp
            )
            gse_df_subset_other = gse_df[gse_df.entrytype != "GSE"]
            # Filter out NaN values from study_accession before converting to SRP
            srx = gse_df_subset_other.study_accession.dropna().tolist()
            srp_df = self.srx_to_srp(srx)
            srp_unique = list(
                set(srp_df.study_accession.unique()).difference(
                    gse_df_subset_gse.study_accession.tolist()
                )
            )
            # Handle mismatched lengths between GSEs and SRPs
            # Create all combinations of GSE-SRP pairs
            gse_srp_pairs = []
            for gse_id in gse_of_interest:
                for srp_id in srp_unique:
                    gse_srp_pairs.append(
                        {"study_alias": gse_id, "study_accession": srp_id}
                    )

            if gse_srp_pairs:
                new_gse_df = pd.DataFrame(gse_srp_pairs)
            else:
                # If no pairs, create empty DataFrame with correct columns
                new_gse_df = pd.DataFrame(columns=["study_alias", "study_accession"])
            # Filter out GSE entries with NaN study_accession before concatenating
            # as we've already created new pairs for them
            gse_df_subset_gse_valid = gse_df_subset_gse[
                gse_df_subset_gse.study_accession.notna()
            ]
            gse_df_subset = pd.concat([gse_df_subset_gse_valid, new_gse_df])
        gse_df_subset = gse_df_subset.loc[gse_df_subset.study_alias.isin(gse)]
        return gse_df_subset[["study_alias", "study_accession"]].drop_duplicates()

    def gsm_to_srp(self, gsm, **kwargs):
        gsm_df = self.fetch_gds_results(gsm, **kwargs)
        gsm_df = gsm_df[gsm_df.entrytype == "GSE"]
        gsm_df = gsm_df.rename(
            columns={"accession": "experiment_alias", "SRA": "study_accession"}
        )
        return gsm_df[["experiment_alias", "study_accession"]].drop_duplicates()

    def gsm_to_srr(self, gsm, **kwargs):
        gsm_df = self.fetch_gds_results(gsm, **kwargs)
        gsm_df = gsm_df.rename(
            columns={
                "accession": "experiment_alias",
                "SRA": "experiment_accession",
                "title": "experiment_title",
                "summary": "sample_attribute",
            }
        )
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"]
        srr_df = self.srx_to_srr(gsm_df.experiment_accession.tolist())
        gsm_df = gsm_df.merge(srr_df, on="experiment_accession")
        return gsm_df[["experiment_alias", "run_accession"]]

    def gsm_to_srs(self, gsm, **kwargs):
        """Get SRS for a GSM"""
        gsm_df = self.fetch_gds_results(gsm, **kwargs)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"].rename(
            columns={"SRA": "experiment_accession", "accession": "experiment_alias"}
        )
        srx = gsm_df.experiment_accession.tolist()
        time.sleep(self.sleep_time)
        srs_df = self.srx_to_srs(srx)
        gsm_df = srs_df.merge(gsm_df, on="experiment_accession")[
            ["experiment_alias", "sample_accession"]
        ]
        return gsm_df.drop_duplicates()

    def gsm_to_srx(self, gsm, **kwargs):
        """Get SRX for a GSM"""
        if isinstance(gsm, str):
            gsm = [gsm]
        gsm_df = self.fetch_gds_results(gsm, **kwargs)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"].rename(
            columns={"SRA": "experiment_accession", "accession": "experiment_alias"}
        )
        gsm_df = gsm_df.loc[gsm_df["experiment_alias"].isin(gsm)]
        return gsm_df[["experiment_alias", "experiment_accession"]].drop_duplicates()

    def gsm_to_gse(self, gsm, **kwargs):
        if isinstance(gsm, str):
            gsm = [gsm]
        if not gsm:  # Handle empty input
            return pd.DataFrame(columns=["study_alias", "study_accession"])

        gsm_df = self.fetch_gds_results(gsm, **kwargs)
        if gsm_df is None or gsm_df.empty:  # Handle case where no results found
            return pd.DataFrame(columns=["study_alias", "study_accession"])

        # For GSM queries, we need to extract GSE IDs from the 'gse' column
        # The entrytype will be 'GSM', not 'GSE'
        gsm_entries = gsm_df[gsm_df.entrytype == "GSM"]

        if gsm_entries.empty:
            return pd.DataFrame(columns=["study_alias", "study_accession"])

        # Extract GSE IDs from the 'gse' column and create result rows
        results = []
        for _, row in gsm_entries.iterrows():
            gsm_id = row["accession"]
            gse_str = str(row.get("gse", ""))

            if gse_str and gse_str != "nan":
                # Handle multiple GSE IDs separated by semicolon
                gse_ids = [
                    gse_id.strip() for gse_id in gse_str.split(";") if gse_id.strip()
                ]
                for gse_id in gse_ids:
                    if gse_id.isdigit():
                        # Add GSE prefix if it's just a number
                        gse_id = f"GSE{gse_id}"
                    results.append(
                        {
                            "study_alias": gse_id,
                            "study_accession": row.get("SRA", pd.NA),
                        }
                    )

        if results:
            result_df = pd.DataFrame(results)
            return result_df[["study_alias", "study_accession"]].drop_duplicates()
        else:
            return pd.DataFrame(columns=["study_alias", "study_accession"])

    def srp_to_gse(self, srp, **kwargs):
        """Get GSE for a SRP"""
        srp_df = self.fetch_gds_results(srp, **kwargs)
        if srp_df is None:
            srp_df = pd.DataFrame(
                {"study_alias": [], "study_accession": [], "entrytype": []}
            )

        srp_df = srp_df.rename(
            columns={"accession": "study_alias", "SRA": "study_accession"}
        )
        srp_df_gse = srp_df[srp_df.entrytype == "GSE"]
        missing_srp = list(set(srp).difference(srp_df_gse.study_accession.tolist()))
        srp_df_nongse = srp_df[srp_df.entrytype != "GSE"]
        if srp_df_nongse.shape[0] >= 1:
            srp_df_nongse = pd.DataFrame(
                {
                    "study_accession": missing_srp,
                    "study_alias": [pd.NA] * len(missing_srp),
                    "entrytpe": ["GSE"] * len(missing_srp),
                }
            )
        srp_df = pd.concat([srp_df_gse, srp_df_nongse])
        return srp_df[["study_accession", "study_alias"]].drop_duplicates()

    def srp_to_srr(self, srp, **kwargs):
        """Get SRR for a SRP"""
        srp_df = self.sra_metadata(srp, **kwargs)
        return _order_first(srp_df, ["study_accession", "run_accession"])

    def srp_to_srs(self, srp, **kwargs):
        """Get SRS for a SRP"""
        srp_df = self.sra_metadata(srp, **kwargs)
        return _order_first(srp_df, ["study_accession", "sample_accession"])

    def srp_to_srx(self, srp, **kwargs):
        """Get SRX for a SRP"""
        srp_df = self.sra_metadata(srp, **kwargs)
        srp_df["study_accesssion"] = srp
        return _order_first(srp_df, ["study_accession", "experiment_accession"])

    def srr_to_gsm(self, srr, **kwargs):
        """Get GSM for a SRR"""
        if isinstance(srr, str):
            srr = [srr]
        srr_df = self.srr_to_srp(srr, detailed=True)
        # remove NAs
        srp = [x for x in srr_df.study_accession.tolist() if not x is pd.NA]
        gse_df = self.fetch_gds_results(srp, **kwargs)
        gse_df = gse_df[gse_df.entrytype == "GSE"].rename(
            columns={"SRA": "project_accession", "accession": "project_alias"}
        )
        gsm_df = self.gse_to_gsm(gse_df.project_alias.tolist(), detailed=True)
        srr_cols = list(
            set(srr_df.columns.tolist()).difference(gsm_df.columns.tolist())
        ) + ["experiment_accession"]
        joined_df = gsm_df.merge(srr_df[srr_cols], on="experiment_accession")
        df = _order_first(joined_df, ["run_accession", "experiment_alias"])
        df = df.loc[df["run_accession"].isin(srr)]
        return df

    def srr_to_srp(self, srr, **kwargs):
        """Get SRP for a SRR"""
        if isinstance(srr, str):
            srr = [srr]
        srr_df = self.sra_metadata(srr, **kwargs)
        if kwargs and kwargs["detailed"] == True:
            return srr_df
        srr_df = srr_df.loc[srr_df["run_accession"].isin(srr)]
        return _order_first(srr_df, ["run_accession", "study_accession"])

    def srr_to_srs(self, srr, **kwargs):
        """Get SRS for a SRR"""
        if isinstance(srr, str):
            srr = [srr]
        srr_df = self.sra_metadata(srr, **kwargs)
        srr_df = srr_df.loc[srr_df["run_accession"].isin(srr)]
        return _order_first(srr_df, ["run_accession", "sample_accession"])

    def srr_to_srx(self, srr, **kwargs):
        """Get SRX for a SRR"""
        if isinstance(srr, str):
            srr = [srr]
        srr_df = self.sra_metadata(srr)
        srr_df = srr_df.loc[srr_df["run_accession"].isin(srr)]
        return _order_first(srr_df, ["run_accession", "experiment_accession"])

    def srs_to_gsm(self, srs, **kwargs):
        """Get GSM for a SRS"""
        if isinstance(srs, str):
            srs = [srs]
        srx_df = self.srs_to_srx(srs)
        time.sleep(self.sleep_time)
        gsm_df = self.srx_to_gsm(srx_df.experiment_accession.tolist(), **kwargs)
        srs_df = srx_df.merge(gsm_df, on="experiment_accession")
        srs_df = srs_df.loc[srs_df["sample_accession"].isin(srs)]
        return _order_first(srs_df, ["sample_accession", "experiment_alias"])

    def srx_to_gsm(self, srx, **kwargs):
        if isinstance(srx, str):
            srx = [srx]
        gsm_df = self.fetch_gds_results(srx, **kwargs)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"].rename(
            columns={"SRA": "experiment_accession", "accession": "experiment_alias"}
        )
        gsm_df = gsm_df.loc[gsm_df["experiment_accession"].isin(srx)]
        return gsm_df[["experiment_accession", "experiment_alias"]].drop_duplicates()

    def srs_to_srx(self, srs, **kwargs):
        """Get SRX for a SRS"""
        srs_df = self.sra_metadata(srs, **kwargs)
        return _order_first(srs_df, ["sample_accession", "experiment_accession"])

    def srx_to_srp(self, srx, **kwargs):
        """Get SRP for a SRX"""
        srx_df = self.sra_metadata(srx, **kwargs)
        return _order_first(srx_df, ["experiment_accession", "study_accession"])

    def srx_to_srr(self, srx, **kwargs):
        """Get SRR for a SRX"""
        srx_df = self.sra_metadata(srx, **kwargs)
        return _order_first(srx_df, ["experiment_accession", "run_accession"])

    def srx_to_srs(self, srx, **kwargs):
        """Get SRS for a SRX"""
        srx_df = self.sra_metadata(srx, **kwargs)
        return _order_first(srx_df, ["experiment_accession", "sample_accession"])

    def search(self, query: str, detailed: bool = False, max: int = 20) -> pd.DataFrame:
        instance = SraSearch(
            verbosity=3 if detailed else 2,
            query=query,
            return_max=max,
            progress_disabled=True,
        )
        instance.search()
        return instance.get_df()[["experiment_accession", "experiment_title"]]

    def _bioproject_uid(self, bioproject):
        """Resolve a BioProject accession to its NCBI numeric UID.

        Parameters
        ----------
        bioproject: str
                   BioProject accession (e.g. PRJNA123456, PRJEB39301, PRJDB13786)

        Returns
        -------
        uid: str or None
            The numeric UID, or None when NCBI holds no such project.
        """
        try:
            response = self._send_retryable_request(
                self.base_url["esearch"],
                params={
                    "db": "bioproject",
                    "term": f"{bioproject}[Project Accession]",
                    "retmode": "json",
                },
            )
            idlist = response.json().get("esearchresult", {}).get("idlist", [])
            return idlist[0] if idlist else None
        except Exception:
            return None

    def fetch_bioproject_pmids(self, bioprojects):
        """Fetch PMIDs for given BioProject accessions

        Parameters
        ----------
        bioprojects: list or str
                    BioProject accession(s)

        Returns
        -------
        bioproject_pmids: dict
                         Mapping of BioProject to list of PMIDs
        """
        if isinstance(bioprojects, str):
            bioprojects = [bioprojects]

        bioproject_pmids = {}
        for bioproject in bioprojects:
            if pd.isna(bioproject) or not bioproject:
                bioproject_pmids[bioproject] = []
                continue

            try:
                uid = self._bioproject_uid(bioproject)
                if not uid:
                    bioproject_pmids[bioproject] = self._search_pmc_by_bioproject(
                        bioproject
                    )
                    time.sleep(self.sleep_time)
                    continue

                payload = self.efetch_params.copy()
                payload = [param for param in payload if param[0] != "retmode"]
                payload += [
                    ("db", "bioproject"),
                    ("id", uid),
                    ("retmode", "xml"),
                ]

                request = self._send_retryable_request(
                    self.base_url["efetch"], params=OrderedDict(payload)
                )
                xml_text = request.text.strip()

                # Parse XML to extract Publication IDs
                pmids = []
                try:
                    xml_dict = xmltodict.parse(
                        xml_text, process_namespaces=False, dict_constructor=OrderedDict
                    )

                    # Navigate through the XML structure
                    if "RecordSet" in xml_dict:
                        records = xml_dict["RecordSet"].get("DocumentSummary", [])
                        if not isinstance(records, list):
                            records = [records]

                        for record in records:
                            project = record.get("Project", {})

                            archive = (
                                project.get("ProjectID", {}).get("ArchiveID", {}) or {}
                            )
                            got = archive.get("@accession")
                            if got and got != bioproject:
                                warnings.warn(
                                    f"BioProject {bioproject} resolved to {got}; "
                                    "discarding its publications"
                                )
                                continue

                            project_descr = project.get("ProjectDescr", {})
                            publications = project_descr.get("Publication", [])

                            if not isinstance(publications, list):
                                publications = [publications]

                            for pub in publications:
                                if isinstance(pub, dict):
                                    pub_id = pub.get("@id", "")
                                elif isinstance(pub, str):
                                    pub_id = pub
                                else:
                                    pub_id = ""

                                if pub_id and pub_id.isdigit():
                                    pmids.append(pub_id)

                except ExpatError:
                    if f'accession="{bioproject}"' in xml_text:
                        pmid_pattern = r'id="(\d+)"'
                        matches = re.findall(pmid_pattern, xml_text)
                        pmids = [
                            match for match in matches if len(match) >= 7
                        ]  # PMIDs are typically 7+ digits
                    else:
                        pmids = []

                # If no PMIDs found in bioproject XML, try searching PMC by bioproject ID
                if not pmids:
                    pmids = self._search_pmc_by_bioproject(bioproject)

                bioproject_pmids[bioproject] = list(set(pmids))  # Remove duplicates
                time.sleep(self.sleep_time)

            except Exception as e:
                warnings.warn(f"Failed to fetch PMIDs for BioProject {bioproject}: {e}")
                bioproject_pmids[bioproject] = []

        return bioproject_pmids

    def srp_to_pmid(self, srp_accessions, detailed=False):
        """Get PMIDs associated with SRP accessions

        Parameters
        ----------
        srp_accessions: list or str
                       SRP accession(s)
        detailed: bool
                 If True, include publication metadata (title, journal, doi, pub_date, authors)

        Returns
        -------
        srp_pmid_df: pandas.DataFrame
                    DataFrame with SRP accessions and associated PMIDs
        """
        if isinstance(srp_accessions, str):
            srp_accessions = [srp_accessions]

        # Get metadata to extract BioProject information
        metadata_df = self.sra_metadata(srp_accessions)
        if metadata_df is None or metadata_df.empty:
            return pd.DataFrame(columns=["srp_accession", "bioproject", "pmid", "doi"])

        # Try to get PMIDs via BioProject first
        unique_bioprojects = metadata_df["bioproject"].dropna().unique().tolist()
        bioproject_pmids = self.fetch_bioproject_pmids(unique_bioprojects)

        results = []
        title_hits = {}  # study_title -> (pmid, doi)
        for _, row in metadata_df.iterrows():
            srp_acc = self._extract_sra_accession(row)
            bioproject = row.get("bioproject", "")

            pmids = bioproject_pmids.get(bioproject, [])

            # Fallback must run per-accession
            if not pmids and srp_acc:
                pmids = self._search_fallback_pmids(
                    [srp_acc]
                ) or self._search_europepmc(srp_acc)

            if pmids:
                pmid, doi = self._publication_for(pmids, "")
            else:
                # sra_metadata is one row per run; search each title once
                title = row.get("study_title", "")
                if title not in title_hits:
                    title_hits[title] = self._publication_for([], title)
                pmid, doi = title_hits[title]

            results.append(
                {
                    "srp_accession": srp_acc,
                    "bioproject": bioproject,
                    "pmid": pmid,
                    "doi": doi,
                }
            )

        result_df = pd.DataFrame(results).drop_duplicates()

        if detailed:
            result_df = self._enrich_with_publication_metadata(result_df)

        return result_df

    def _search_fallback_pmids(self, srp_accessions):
        """Search for PMIDs using fallback strategies (external sources + direct SRA search + GSE search)"""
        try:
            original_sleep = self.sleep_time
            self.sleep_time = max(0.1, self.sleep_time * 0.5)

            # Strategy 1: Search via external source identifiers
            # Example: ERP018009
            detailed_metadata = self.sra_metadata(
                srp_accessions, detailed=True, include_pmids=False
            )
            if detailed_metadata is not None and not detailed_metadata.empty:
                if external_sources := self.extract_external_sources(detailed_metadata):
                    pmids = self.search_pmc_for_external_sources([external_sources[0]])
                    if pmids:
                        return pmids

                # Strategy 2: Search via GSE identifiers extracted from metadata
                # Example: GSE253406 --> SRP484103
                gse_pmids = self._search_gse_gsm_pmids(
                    detailed_metadata, srp_accessions
                )
                if gse_pmids:
                    return gse_pmids

            # Strategy 3: Direct SRP ID search
            # Example: SRP047086
            pmids = self.search_pmc_for_external_sources(srp_accessions)
            return pmids

        except Exception as e:
            return []
        finally:
            self.sleep_time = original_sleep

    def _extract_sra_accession(self, row):
        """Extract SRA accession from metadata row"""
        return row.get(
            "study_accession",
            row.get(
                "run_accession",
                row.get("experiment_accession", row.get("sample_accession", "")),
            ),
        )

    def _get_smallest_pmid(self, pmids):
        """Get the numerically smallest PMID from a list"""
        if not pmids:
            return pd.NA

        # Convert to integers for proper numeric sorting
        pmid_ints = []
        for pmid in pmids:
            try:
                pmid_ints.append(int(pmid))
            except ValueError:
                pmid_ints.append(pmid)  # Keep non-numeric as-is

        return str(min(pmid_ints))

    def _geo_title(self, gse_acc):
        """Fetch the GEO series title for a GSE accession, empty if unknown"""
        try:
            r = self._send_retryable_request(
                self.base_url["esearch"],
                params={"db": "gds", "term": f"{gse_acc}[ACCN]", "retmode": "json"},
            )
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return ""
            r2 = self._send_retryable_request(
                self.base_url["esummary"],
                params={"db": "gds", "id": ids[0], "retmode": "json"},
            )
            return r2.json().get("result", {}).get(ids[0], {}).get("title") or ""
        except Exception:
            return ""

    def _publication_for(self, pmids, title):
        """Resolve a study to a PMID, falling back to a title search

        Parameters
        ----------
        pmids: list
               PMIDs found by accession-linked lookups (may be empty)
        title: str
               Study title, searched only when pmids is empty

        Returns
        -------
        (pmid, doi): tuple of str or pandas.NA
        """
        if pmids:
            return self._get_smallest_pmid(pmids), pd.NA
        return self._search_publication_by_title(title)

    def _bioproject_title(self, bp_id):
        """Fetch the study title for a BioProject UID, empty if unknown"""
        try:
            r = self._send_retryable_request(
                self.base_url["esummary"],
                params={"db": "bioproject", "id": bp_id, "retmode": "json"},
            )
            record = r.json().get("result", {}).get(str(bp_id), {})
            return record.get("project_title") or ""
        except Exception:
            return ""

    def _arrayexpress_title(self, ae_acc):
        """Fetch the study title for an ArrayExpress accession via BioStudies"""
        try:
            r = self._send_retryable_request(
                f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{ae_acc}"
            )
            r.raise_for_status()
            for attr in r.json().get("attributes", []):
                if attr.get("name", "").lower() == "title":
                    return attr.get("value") or ""
        except Exception:
            pass
        return ""

    def _search_publication_by_title(self, title):
        """Find a study's publication by title

        Europe PMC indexes MEDLINE, PMC and preprint servers (bioRxiv/medRxiv,
        source PPR) in one title index. Preprint-only studies resolve here with a
        DOI and no PMID.

        Parameters
        ----------
        title: str
               Study title (e.g. study_title from sra_metadata or a GEO title)

        Returns
        -------
        (pmid, doi): tuple of str or pandas.NA
        """
        if not title:
            return pd.NA, pd.NA
        candidates = [title]
        # SRA/GEO truncate long titles, leaving a half word the phrase match trips on
        if len(title) >= TRUNCATED_TITLE_LENGTH and " " in title:
            candidates.append(title.rsplit(" ", 1)[0])
        for query_title in candidates:
            hits = self._epmc_search(f'TITLE:"{query_title}"', page_size=5)
            # a since-published preprint appears twice; the journal version has the PMID
            for hit in sorted(hits, key=lambda h: not h.get("pmid")):
                pmid, doi = hit.get("pmid"), hit.get("doi")
                if not pmid and doi:
                    # EPMC omits the PMID on some records PubMed does index
                    pmid = self.doi_to_pmid(doi).get(doi)
                if pmid or doi:
                    return pmid or pd.NA, doi or pd.NA
        return pd.NA, pd.NA

    def _search_pubmed_by_title(self, title):
        """Resolve a study title to PMIDs via PubMed

        Covers recent studies not yet linked to their paper in PMC/Europe PMC.
        """
        if not title:
            return []
        try:
            r3 = self._send_retryable_request(
                self.base_url["esearch"],
                params={"db": "pubmed", "term": f"{title}[Title]", "retmode": "json"},
            )
            return r3.json().get("esearchresult", {}).get("idlist", [])
        except Exception:
            return []

    def _epmc_search(self, query, result_type="lite", page_size=1):
        """Run a Europe PMC search; empty list on failure"""
        try:
            r = self._send_retryable_request(
                self.base_url["europepmc"],
                params={
                    "query": query,
                    "resultType": result_type,
                    "format": "json",
                    "pageSize": page_size,
                },
            )
            r.raise_for_status()
            hits = r.json().get("resultList", {}).get("result", [])
        except Exception:
            return []
        time.sleep(self.sleep_time)
        return hits

    def _search_europepmc(self, query):
        """Search Europe PMC for PMIDs matching a query string

        Parameters
        ----------
        query: str
               Search query (e.g. an accession like 'SRP033481' or 'GSE12345')

        Returns
        -------
        pmids: list
              List of PMIDs found
        """
        hits = self._epmc_search(f'"{query}"', page_size=10)
        return [h["pmid"] for h in hits if h.get("pmid") and h["pmid"].isdigit()]

    def pmid_info(self, ids, detailed=False, skip_journal_metrics=False):
        """Get publication metadata and journal metrics for PMIDs, PMCIDs, or DOIs.

        Parameters
        ----------
        ids: list or str
             PMID(s), PMCID(s) (e.g. PMC4589343), or DOI(s)
        detailed: bool
                 If True, also look up associated GEO/SRA datasets.
        skip_journal_metrics: bool
                 If True, skip the OpenAlex journal metrics lookup (h-index,
                 i10-index, etc.). Citation counts are still fetched per-PMID.
                 Useful for large batch runs since citation lookups are free
                 singleton requests while journal metrics use paid list/search
                 requests on the OpenAlex API.

        Returns
        -------
        DataFrame with publication metadata, journal metrics, citation count,
        and (when detailed) associated GEO/SRA accessions.
        """
        if isinstance(ids, str):
            ids = [ids]

        resolved = [
            {"input_id": raw_id, "pmid": self._resolve_to_pmid(raw_id.strip())}
            for raw_id in ids
        ]

        result_df = pd.DataFrame(resolved)
        if result_df.empty:
            return result_df

        valid_pmids = self._valid_pmids(result_df)
        if not valid_pmids:
            return result_df

        meta_df = self.fetch_pmid_metadata(valid_pmids)
        if not meta_df.empty:
            result_df["pmid"] = result_df["pmid"].astype(str)
            result_df = result_df.merge(meta_df, on="pmid", how="left")
            if skip_journal_metrics:
                for col in self._JOURNAL_METRIC_COLS:
                    if col not in result_df.columns:
                        result_df[col] = pd.NA
            else:
                result_df = self.fetch_journal_metrics(result_df)

        if detailed:
            datasets = [self._find_datasets_for_pmid(p) for p in valid_pmids]
            ds_df = pd.DataFrame(datasets, columns=["gse", "srp"])
            ds_df["pmid"] = valid_pmids
            result_df = result_df.merge(ds_df, on="pmid", how="left")

        if (
            "input_id" in result_df.columns
            and (result_df["input_id"] == result_df["pmid"]).all()
        ):
            result_df = result_df.drop(columns=["input_id"])

        return result_df

    def _resolve_to_pmid(self, raw_id):
        """Resolve a PMID, PMCID, or DOI to a PMID string via Europe PMC."""
        if raw_id.upper().startswith("PMC"):
            query = f"PMCID:{raw_id}"
        elif "/" in raw_id:
            query = f"DOI:{raw_id}"
        elif raw_id.isdigit():
            query = f"ext_id:{raw_id} src:med"
        else:
            query = f'"{raw_id}"'
        hits = self._epmc_search(query)
        if hits and hits[0].get("pmid"):
            return hits[0]["pmid"]
        return pd.NA

    def _ncbi_params(self, params):
        """Return params dict with api_key injected if available."""
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def _elink_ids(self, pmid, db, linkname):
        """Get linked database IDs for a PMID via NCBI elink."""
        r = self._send_retryable_request(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi",
            params=self._ncbi_params(
                {"dbfrom": "pubmed", "db": db, "id": pmid, "retmode": "json"}
            ),
        )
        r.raise_for_status()
        for ls in r.json().get("linksets", []):
            for ldb in ls.get("linksetdbs", []):
                if ldb.get("linkname") == linkname:
                    return [str(lid) for lid in ldb.get("links", [])]
        return []

    def _find_datasets_for_pmid(self, pmid):
        """Find GEO and SRA accessions linked to a PMID via NCBI elink.

        Returns (gse, srp) where each is a comma-separated string of accessions.
        """
        gse, srp = "", ""
        try:
            gds_ids = self._elink_ids(pmid, "gds", "pubmed_gds")
            if gds_ids:
                r = self._send_retryable_request(
                    self.base_url["esummary"],
                    params=self._ncbi_params(
                        {"db": "gds", "id": ",".join(gds_ids[:5]), "retmode": "json"}
                    ),
                )
                r.raise_for_status()

                data = r.json().get("result", {})
                gse_accs = {
                    data.get(gid, {}).get("accession", "") for gid in gds_ids[:5]
                }
                gse = ", ".join(sorted(a for a in gse_accs if a.startswith("GSE")))

            time.sleep(self.sleep_time)

            sra_ids = self._elink_ids(pmid, "sra", "pubmed_sra")
            if sra_ids:
                r = self._send_retryable_request(
                    self.base_url["esummary"],
                    params=self._ncbi_params(
                        {"db": "sra", "id": ",".join(sra_ids[:5]), "retmode": "json"}
                    ),
                )
                r.raise_for_status()

                data = r.json().get("result", {})
                srp_accs = set()
                for sid in sra_ids[:5]:
                    srp_accs.update(
                        re.findall(
                            r'acc="(SRP\d+)"', data.get(sid, {}).get("expxml", "")
                        )
                    )

                srp = ", ".join(sorted(srp_accs))
            time.sleep(self.sleep_time)
        except Exception:
            pass
        return gse, srp

    @staticmethod
    def _valid_pmids(df):
        """Extract valid PMID strings from a DataFrame's pmid column."""
        return [
            p
            for p in df["pmid"].dropna().astype(str).tolist()
            if p not in ("<NA>", "nan")
        ]

    def _enrich_with_publication_metadata(self, result_df):
        """Merge publication metadata and journal metrics into a PMID result DataFrame."""
        if result_df.empty:
            return result_df
        valid_pmids = self._valid_pmids(result_df)
        if not valid_pmids:
            return result_df
        meta_df = self.fetch_pmid_metadata(valid_pmids)
        if meta_df.empty:
            return result_df
        result_df["pmid"] = result_df["pmid"].astype(str)
        result_df = result_df.merge(meta_df, on="pmid", how="left")
        return self.fetch_journal_metrics(result_df)

    _PMID_META_COLS = [
        "pmid",
        "title",
        "journal",
        "doi",
        "pub_date",
        "authors",
        "issn",
        "citation_count",
    ]

    _JOURNAL_METRIC_COLS = [
        "journal_h_index",
        "journal_i10_index",
        "journal_2yr_mean_citedness",
        "journal_cited_by_count",
        "journal_works_count",
    ]

    def fetch_pmid_metadata(self, pmids):
        """Fetch publication metadata for PMIDs.

        Parameters
        ----------
        pmids: list or str
               PMID(s)

        Returns
        -------
        DataFrame with columns: pmid, title, journal, doi, pub_date, authors,
                                issn, citation_count
        """
        if isinstance(pmids, str):
            pmids = [pmids]
        pmids = [str(p) for p in pmids if str(p) not in ("<NA>", "nan")]
        if not pmids:
            return pd.DataFrame(columns=self._PMID_META_COLS)

        results = {}
        self._fetch_pmid_metadata_ncbi(pmids, results)

        for pmid in (p for p in pmids if p not in results):
            self._fetch_pmid_metadata_epmc(pmid, results)

        if not results:
            return pd.DataFrame(columns=self._PMID_META_COLS)

        for pmid, entry in results.items():
            try:
                entry["citation_count"] = self._fetch_citation_count(
                    pmid, entry.get("doi", "")
                )
            except OpenAlexError as e:
                if self.verbose:
                    print(
                        f"Warning: failed to fetch citation count from OpenAlex for PMID={pmid}, "
                        f"DOI={entry.get('doi', '')}: {e}",
                        file=sys.stderr,
                    )
                entry["citation_count"] = pd.NA

        return pd.DataFrame([results[p] for p in pmids if p in results])

    def _fetch_pmid_metadata_ncbi(self, pmids, results):
        """Batch-query NCBI PubMed efetch for full author names, populating *results* in-place."""
        try:
            r = self._send_retryable_request(
                self.base_url["efetch"],
                params=self._ncbi_params(
                    {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
                ),
            )
            r.raise_for_status()
            xml_text = re.sub(r"<!DOCTYPE[^>]*>", "", r.content.decode("utf-8"))
            root = ET.fromstring(xml_text)
        except Exception:
            return

        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID", "")
            if not pmid:
                continue

            journal_el = article.find(".//Journal")
            pub_date = journal_el.find(".//PubDate") if journal_el is not None else None
            date_parts = []
            if pub_date is not None:
                medline_date = pub_date.findtext("MedlineDate", "")
                if medline_date:
                    date_parts = [medline_date]
                else:
                    for field in ("Year", "Month", "Day"):
                        val = pub_date.findtext(field, "")
                        if val:
                            date_parts.append(val)

            doi_els = [
                e for e in article.findall(".//ArticleId") if e.get("IdType") == "doi"
            ]
            authors = ", ".join(
                f"{a.findtext('ForeName', '')} {a.findtext('LastName', '')}".strip()
                for a in article.findall(".//Author")
                if a.findtext("LastName")
            )

            # itertext() keeps text after inline markup (<i>, <sub>); findtext truncates at it.
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""

            results[pmid] = {
                "pmid": pmid,
                "title": title,
                "journal": (
                    journal_el.findtext("Title", "") if journal_el is not None else ""
                ),
                "doi": doi_els[0].text if doi_els else "",
                "pub_date": " ".join(date_parts),
                "authors": authors,
                "issn": (
                    journal_el.findtext("ISSN", "") if journal_el is not None else ""
                ),
            }

    def _fetch_pmid_metadata_epmc(self, pmid, results):
        """Query Europe PMC for a single PMID, populating *results* dict in-place."""
        try:
            hits = self._epmc_search(f"ext_id:{pmid} src:med", result_type="core")
            if hits:
                hit = hits[0]
                journal_obj = hit.get("journalInfo", {}).get("journal", {})
                author_list = hit.get("authorList", {}).get("author", [])
                if author_list:
                    authors = ", ".join(
                        f"{a.get('firstName', '')} {a.get('lastName', '')}".strip()
                        for a in author_list
                        if a.get("lastName")
                    )
                else:
                    authors = hit.get("authorString", "")
                results[pmid] = {
                    "pmid": pmid,
                    "title": hit.get("title", ""),
                    "journal": hit.get("journalTitle") or journal_obj.get("title", ""),
                    "doi": hit.get("doi", ""),
                    "pub_date": hit.get("firstPublicationDate", ""),
                    "authors": authors,
                    "issn": journal_obj.get("essn", "") or journal_obj.get("issn", ""),
                }
        except Exception:
            pass

    def _openalex_request(self, url, params=None, retries=None, timeout=None):
        """Make an authenticated OpenAlex API request.

        Raises
        ------
        OpenAlexError
            On HTTP 429 (rate limit), 401/403 (auth), or any response whose
            JSON body contains an ``"error"`` key
        """
        if params is None:
            params = {}
        if self.openalex_api_key:
            params["api_key"] = self.openalex_api_key
        if self.openalex_email:
            params["mailto"] = self.openalex_email

        r = self._send_retryable_request(
            url,
            params=params,
            retries=retries,
            timeout=timeout,
            non_retryable_status_codes=(429, 401, 403),
        )

        if r.status_code in (429, 401, 403):
            try:
                body = r.json()
                msg = body.get("message", body.get("error", r.text[:300]))
            except Exception:
                msg = r.text[:300]
            raise OpenAlexError(f"OpenAlex API error (HTTP {r.status_code}): {msg}")
        return r

    def _fetch_citation_count(self, pmid, doi):
        """Get citation count from OpenAlex by DOI (preferred) or PMID.

        Raises
        ------
        OpenAlexError
            If the API returns a rate-limit or authentication error.
        """
        for lookup_id in filter(None, [f"doi:{doi}" if doi else None, f"pmid:{pmid}"]):
            try:
                r = self._openalex_request(
                    f"https://api.openalex.org/works/{lookup_id}"
                )
                if r.status_code == 200:
                    return r.json().get("cited_by_count", pd.NA)
            except OpenAlexError:
                raise
            except Exception:
                pass
        return pd.NA

    def fetch_journal_metrics(self, journal_df):
        """Add OpenAlex journal quality metrics to a DataFrame containing a ``journal`` column.

        Parameters
        ----------
        journal_df: DataFrame with ``journal`` (required) and ``issn`` (optional) columns.

        Returns
        -------
        Same DataFrame with added columns: journal_h_index, journal_i10_index,
        journal_2yr_mean_citedness, journal_cited_by_count, journal_works_count.
        """
        if journal_df.empty or "journal" not in journal_df.columns:
            for col in self._JOURNAL_METRIC_COLS:
                journal_df[col] = pd.NA
            return journal_df

        has_issn = "issn" in journal_df.columns
        if has_issn:
            unique_journals = (
                journal_df[["journal", "issn"]].drop_duplicates().values.tolist()
            )
        else:
            unique_journals = [[j, ""] for j in journal_df["journal"].dropna().unique()]

        cache = {}
        for journal_name, issn in unique_journals:
            if not journal_name or journal_name in cache:
                continue
            try:
                cache[journal_name] = self._openalex_source_lookup(issn, journal_name)
            except OpenAlexError as e:
                if self.verbose:
                    print(
                        f"Warning: failed to fetch journal metrics from OpenAlex "
                        f"for journal={journal_name}, issn={issn}: {e}",
                        file=sys.stderr,
                    )
                cache[journal_name] = dict.fromkeys(self._JOURNAL_METRIC_COLS, pd.NA)

        for col in self._JOURNAL_METRIC_COLS:
            journal_df[col] = journal_df["journal"].map(
                lambda j, c=col: cache.get(j, {}).get(c, pd.NA)
            )
        return journal_df

    def _openalex_source_lookup(self, issn, journal_name):
        """Look up a journal in OpenAlex by ISSN then name. Returns metrics dict.

        Raises
        ------
        OpenAlexError
            If the API returns a rate-limit or authentication error.
        """
        empty = dict.fromkeys(self._JOURNAL_METRIC_COLS, pd.NA)
        source = None
        try:
            for params in filter(
                None,
                [
                    {"filter": f"issn:{issn}", "per_page": 1} if issn else None,
                    {"search": journal_name, "per_page": 1} if journal_name else None,
                ],
            ):
                r = self._openalex_request(
                    "https://api.openalex.org/sources", params=params
                )
                r.raise_for_status()
                hits = r.json().get("results", [])
                if hits:
                    source = hits[0]
                    break
        except OpenAlexError:
            raise
        except Exception:
            return empty

        if source is None:
            return empty

        stats = source.get("summary_stats", {})
        return {
            "journal_h_index": stats.get("h_index", pd.NA),
            "journal_i10_index": stats.get("i10_index", pd.NA),
            "journal_2yr_mean_citedness": stats.get("2yr_mean_citedness", pd.NA),
            "journal_cited_by_count": source.get("cited_by_count", pd.NA),
            "journal_works_count": source.get("works_count", pd.NA),
        }

    def extract_external_sources(self, metadata_df):
        """Extract external source identifiers from SRA metadata

        Parameters
        ----------
        metadata_df: pandas.DataFrame
                    DataFrame containing SRA metadata

        Returns
        -------
        external_sources: list
                         List of external source identifiers found
        """
        external_sources = []

        patterns = [
            r"E-MTAB-\d+",  # ArrayExpress
            r"GSE\d+",  # GEO Series
            r"E-GEOD-\d+",  # GEO in ArrayExpress
            r"E-MEXP-\d+",  # MEXP in ArrayExpress
            r"E-TABM-\d+",  # TABM in ArrayExpress
        ]

        # Fields that commonly contain external source identifiers
        source_fields = ["run_alias", "submitter id", "sample name", "experiment_alias"]

        for field in source_fields:
            if field in metadata_df.columns:
                values = metadata_df[field].dropna().unique()
                for value in values:
                    value_str = str(value)
                    for pattern in patterns:
                        matches = re.findall(pattern, value_str)
                        external_sources.extend(
                            match for match in matches if match not in external_sources
                        )

        return external_sources

    def _search_gse_gsm_pmids(self, metadata_df, sra_accessions):
        """Search for PMIDs using GSE identifiers from BioProject and SRP conversion

        Parameters
        ----------
        metadata_df: pandas.DataFrame
                    Detailed metadata DataFrame
        sra_accessions: list
                       List of SRA accessions being searched

        Returns
        -------
        pmids: list
              List of PMIDs found via GSE search
        """
        import time

        gse_identifiers = []

        # Strategy 1: BioProject to GSE conversion via NCBI search
        if "bioproject" in metadata_df.columns:
            unique_bioprojects = metadata_df["bioproject"].dropna().unique()
            for bioproject in unique_bioprojects[
                :3
            ]:  # Limit to avoid too many requests
                try:
                    gse_ids = self._bioproject_to_gse(bioproject)
                    gse_identifiers.extend(gse_ids)
                    time.sleep(self.sleep_time)  # Rate limiting
                except Exception:
                    pass

        # Strategy 2: SRP to GSE conversion via NCBI ELink
        for sra_acc in sra_accessions:
            if sra_acc.startswith("SRP"):
                try:
                    gse_ids = self._srp_to_gse_via_elink(sra_acc)
                    gse_identifiers.extend(gse_ids)
                    time.sleep(self.sleep_time)  # Rate limiting
                except Exception:
                    pass

        # Strategy 3: Try existing pysradb SRP to GSE conversion
        for sra_acc in sra_accessions:
            if sra_acc.startswith("SRP"):
                try:
                    gse_df = self.srp_to_gse(sra_acc)
                    if not gse_df.empty and "experiment_alias" in gse_df.columns:
                        gse_values = gse_df["experiment_alias"].dropna().astype(str)
                        for gse_val in gse_values:
                            if gse_val.startswith("GSE"):
                                gse_identifiers.append(gse_val)
                except Exception:
                    pass

        # Remove duplicates and search PMC for GSE identifiers
        unique_gse_ids = list(set(gse_identifiers))

        if unique_gse_ids:
            pmids = self.search_pmc_for_external_sources(unique_gse_ids)
            return pmids

        return []

    def _bioproject_to_gse(self, bioproject):
        """Convert BioProject ID to GSE ID via NCBI search

        Parameters
        ----------
        bioproject: str
                   BioProject ID (e.g., 'PRJNA1065472')

        Returns
        -------
        gse_ids: list
                List of GSE IDs found
        """
        import requests

        gse_ids = []
        try:
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "gds",
                "term": f"{bioproject}[BioProject]",
                "retmode": "json",
                "retmax": "10",
            }

            response = self._send_retryable_request(search_url, params=search_params)
            result = response.json()
            geo_uids = result["esearchresult"]["idlist"]

            if geo_uids:
                # Get summary to find GSE IDs
                summary_url = (
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                )
                summary_params = {
                    "db": "gds",
                    "id": ",".join(geo_uids),
                    "retmode": "json",
                }

                summary_response = self._send_retryable_request(
                    summary_url, params=summary_params
                )
                summary_result = summary_response.json()

                for uid in geo_uids:
                    if uid in summary_result["result"]:
                        record = summary_result["result"][uid]
                        accession = record.get("accession", "")
                        if accession.startswith("GSE"):
                            gse_ids.append(accession)

        except Exception:
            pass

        return gse_ids

    def _srp_to_gse_via_elink(self, srp_id):
        """Convert SRP ID to GSE ID via NCBI ELink

        Parameters
        ----------
        srp_id: str
               SRP ID (e.g., 'SRP484103')

        Returns
        -------
        gse_ids: list
                List of GSE IDs found
        """
        gse_ids = []
        try:
            # First, search for the SRP in SRA database to get UIDs
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "sra",
                "term": srp_id,
                "retmode": "json",
                "retmax": "5",
            }

            response = self._send_retryable_request(search_url, params=search_params)
            result = response.json()
            sra_uids = result["esearchresult"]["idlist"]

            if sra_uids:
                # Use ELink to find related GEO records
                elink_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
                elink_params = {
                    "dbfrom": "sra",
                    "db": "gds",
                    "id": sra_uids[0],  # Use first UID
                    "retmode": "json",
                }

                elink_response = self._send_retryable_request(
                    elink_url, params=elink_params
                )
                elink_result = elink_response.json()

                if "linksets" in elink_result:
                    for linkset in elink_result["linksets"]:
                        if "linksetdbs" in linkset:
                            for linksetdb in linkset["linksetdbs"]:
                                if linksetdb["dbto"] == "gds":
                                    geo_uids = linksetdb["links"]

                                    if geo_uids:
                                        # Get summary to find GSE IDs
                                        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                                        summary_params = {
                                            "db": "gds",
                                            "id": ",".join(geo_uids),
                                            "retmode": "json",
                                        }

                                        summary_response = self._send_retryable_request(
                                            summary_url,
                                            params=summary_params,
                                        )
                                        summary_result = summary_response.json()

                                        for uid in geo_uids:
                                            if uid in summary_result["result"]:
                                                record = summary_result["result"][uid]
                                                accession = record.get("accession", "")
                                                if accession.startswith("GSE"):
                                                    gse_ids.append(accession)

        except Exception:
            pass

        return gse_ids

    def _search_pmc_by_bioproject(self, bioproject_id):
        """Search PubMed Central for PMIDs using BioProject accession ID

        This provides a fallback mechanism when the BioProject XML doesn't contain
        publication metadata but the research has been published and is cited in PMC.

        Parameters
        ----------
        bioproject_id: str
                      BioProject accession ID (e.g., PRJEB39301, PRJNA123456)

        Returns
        -------
        pmids: list
              List of PMIDs found associated with the bioproject
        """
        try:
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pmc",
                "term": bioproject_id,
                "retmode": "json",
                "retmax": "10",
            }

            response = self._send_retryable_request(search_url, params=search_params)
            result = response.json()

            pmc_ids = result.get("esearchresult", {}).get("idlist", [])
            if not pmc_ids:
                return self._search_europepmc(bioproject_id)

            # Get primary PMIDs for each PMC article
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pmc",
                "id": ",".join(pmc_ids),
                "retmode": "json",
            }

            summary_response = self._send_retryable_request(
                summary_url, params=summary_params
            )
            summary_result = summary_response.json()

            pmids = []
            # Extract primary PMID for each PMC article
            for pmc_id in pmc_ids:
                if pmc_id in summary_result.get("result", {}):
                    article = summary_result["result"][pmc_id]
                    articleids = article.get("articleids", [])

                    # Find the primary PMID
                    for aid in articleids:
                        if aid.get("idtype") == "pmid":
                            primary_pmid = aid.get("value")
                            if primary_pmid and primary_pmid not in pmids:
                                pmids.append(primary_pmid)
                            break

            if pmids:
                return pmids

            return self._search_europepmc(bioproject_id)

        except Exception as e:
            # Silently fail and return empty list for fallback mechanism
            return []

    def search_pmc_for_external_sources(self, external_sources):
        """Search PubMed Central for PMIDs using external source identifiers

        Parameters
        ----------
        external_sources: list
                         List of external source identifiers

        Returns
        -------
        pmids: list
              List of PMIDs found
        """
        if not external_sources:
            return []

        all_pmids = []

        for source in external_sources:
            try:
                search_url = (
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                )
                search_params = {
                    "db": "pmc",
                    "term": source,
                    "retmode": "json",
                    "retmax": "10",
                }

                response = self._send_retryable_request(
                    search_url, params=search_params
                )
                result = response.json()

                pmc_ids = result["esearchresult"]["idlist"]
                if not pmc_ids:
                    continue

                # Get primary PMIDs for each PMC article
                summary_url = (
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                )
                summary_params = {
                    "db": "pmc",
                    "id": ",".join(pmc_ids),
                    "retmode": "json",
                }

                summary_response = self._send_retryable_request(
                    summary_url, params=summary_params
                )
                summary_result = summary_response.json()

                # Extract primary PMID for each PMC article
                for pmc_id in pmc_ids:
                    if pmc_id in summary_result["result"]:
                        article = summary_result["result"][pmc_id]
                        articleids = article.get("articleids", [])

                        # Find the primary PMID
                        for aid in articleids:
                            if aid.get("idtype") == "pmid":
                                primary_pmid = aid.get("value")
                                if primary_pmid and primary_pmid not in all_pmids:
                                    all_pmids.append(primary_pmid)
                                break

                time.sleep(self.sleep_time)  # Rate limiting

            except Exception as e:
                continue

        return list(set(all_pmids))  # Remove duplicates

    def sra_to_pmid(self, sra_accessions):
        """Get PMIDs for SRA accessions (backward compatibility wrapper)

        Parameters
        ----------
        sra_accessions: list or str
                       SRA accession(s) - can be SRP, SRR, SRX, or SRS

        Returns
        -------
        sra_pmid_df: pandas.DataFrame
                    DataFrame with SRA accessions and associated PMIDs
        """
        # For SRP accessions, use the main method
        if isinstance(sra_accessions, str):
            if sra_accessions.startswith("SRP"):
                return self.srp_to_pmid(sra_accessions)
        elif isinstance(sra_accessions, list):
            # If all are SRP accessions, use main method
            if all(acc.startswith("SRP") for acc in sra_accessions):
                return self.srp_to_pmid(sra_accessions)

        # For other SRA accessions, convert to SRP first if possible
        # This is a simplified implementation for backward compatibility
        return self.srp_to_pmid(sra_accessions)

    def srr_to_pmid(self, srr):
        """Get PMIDs for Run Accessions (SRR)"""
        return self.sra_to_pmid(srr)

    def srx_to_pmid(self, srx):
        """Get PMIDs for Experiment Accessions (SRX)"""
        return self.sra_to_pmid(srx)

    def srs_to_pmid(self, srs):
        """Get PMIDs for Sample Accessions (SRS)"""
        return self.sra_to_pmid(srs)

    def gse_to_pmid(self, gse_accessions, detailed=False):
        """Get PMIDs for GSE accessions by searching PubMed Central

        Parameters
        ----------
        gse_accessions: list or str
                       GSE accession(s)
        detailed: bool
                 If True, include publication metadata (title, journal, doi, pub_date, authors)

        Returns
        -------
        gse_pmid_df: pandas.DataFrame
                    DataFrame with GSE accessions and associated PMIDs
        """
        if isinstance(gse_accessions, str):
            gse_accessions = [gse_accessions]

        results = []
        for gse_acc in gse_accessions:
            pmids = self.search_pmc_for_external_sources([gse_acc])
            # Fallback: Europe PMC
            if not pmids:
                pmids = self._search_europepmc(gse_acc)
            # fall back to the GEO title, PubMed first then Europe PMC
            title = "" if pmids else self._geo_title(gse_acc)
            if not pmids:
                pmids = self._search_pubmed_by_title(title)

            pmid, doi = self._publication_for(pmids, title)
            results.append({"gse_accession": gse_acc, "pmid": pmid, "doi": doi})

        result_df = pd.DataFrame(results)

        if detailed:
            result_df = self._enrich_with_publication_metadata(result_df)

        return result_df

    def ae_to_pmid(self, ae_accessions):
        """Get PMIDs for ArrayExpress accessions by searching Europe PMC

        Parameters
        ----------
        ae_accessions: list or str
                      ArrayExpress accession(s) (e.g. E-MTAB-*, E-GEOD-*)

        Returns
        -------
        ae_pmid_df: pandas.DataFrame
                   DataFrame with columns [ae_accession, pmid, doi]
        """
        if isinstance(ae_accessions, str):
            ae_accessions = [ae_accessions]

        results = []
        for acc in ae_accessions:
            pmids = self._search_europepmc(acc) or self.search_pmc_for_external_sources(
                [acc]
            )
            title = "" if pmids else self._arrayexpress_title(acc)
            pmid, doi = self._publication_for(pmids, title)
            results.append({"ae_accession": acc, "pmid": pmid, "doi": doi})

        return pd.DataFrame(results)

    def ena_to_pmid(self, ena_accessions):
        """Get PMIDs for ENA/BioProject accessions via NCBI elink

        Uses BioProject → PubMed linkage in NCBI for PRJNA/PRJEB/PRJD
        accessions, with Europe PMC as fallback.

        Parameters
        ----------
        ena_accessions: list or str
                       ENA study accession(s) (e.g. PRJEB*, PRJNA*, PRJD*)

        Returns
        -------
        ena_pmid_df: pandas.DataFrame
                    DataFrame with columns [ena_accession, pmid, doi]
        """
        if isinstance(ena_accessions, str):
            ena_accessions = [ena_accessions]

        results = []
        for acc in ena_accessions:
            pmids, title = [], ""
            try:
                # Step 1: resolve accession to BioProject numeric ID
                r = self._send_retryable_request(
                    self.base_url["esearch"],
                    params={
                        "db": "bioproject",
                        "term": f"{acc}[Project Accession]",
                        "retmode": "json",
                    },
                )
                bp_ids = r.json().get("esearchresult", {}).get("idlist", [])

                if bp_ids:
                    # Step 2: elink BioProject → PubMed
                    r2 = self._send_retryable_request(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi",
                        params={
                            "dbfrom": "bioproject",
                            "db": "pubmed",
                            "id": bp_ids[0],
                            "retmode": "json",
                        },
                    )
                    for ls in r2.json().get("linksets", []):
                        for ldb in ls.get("linksetdbs", []):
                            pmids.extend(str(x) for x in ldb.get("links", []))

                # fall back to Europe PMC, then the BioProject title
                if not pmids:
                    pmids = self._search_europepmc(acc)
                if not pmids and bp_ids:
                    title = self._bioproject_title(bp_ids[0])

                time.sleep(self.sleep_time)

            except Exception:
                pass

            pmid, doi = self._publication_for(pmids, title)
            results.append({"ena_accession": acc, "pmid": pmid, "doi": doi})

        return pd.DataFrame(results)

    def doi_to_pmid(self, dois):
        """Convert DOI(s) to PMID(s)

        Parameters
        ----------
        dois: list or str
             DOI(s)

        Returns
        -------
        doi_pmid_mapping: dict
                         Mapping of DOI to PMID
        """
        if isinstance(dois, str):
            dois = [dois]

        doi_pmid_mapping = {}

        for doi in dois:
            try:
                search_url = self.base_url["esearch"]
                search_params = {
                    "db": "pubmed",
                    "term": f"{doi}[DOI]",
                    "retmode": "json",
                }

                response = self._send_retryable_request(
                    search_url, params=search_params
                )
                result = response.json()

                id_list = result.get("esearchresult", {}).get("idlist", [])
                if id_list:
                    doi_pmid_mapping[doi] = id_list[0]
                else:
                    doi_pmid_mapping[doi] = None

                time.sleep(self.sleep_time)

            except requests.RequestException as e:
                warnings.warn(f"Network error while getting PMID for DOI {doi}: {e}")
                doi_pmid_mapping[doi] = None
            except ValueError as e:
                warnings.warn(
                    f"Value error while processing response for DOI {doi}: {e}"
                )
                doi_pmid_mapping[doi] = None

        return doi_pmid_mapping

    def _send_retryable_request(
        self,
        url,
        params=None,
        data=None,
        retries=None,
        timeout=None,
        non_retryable_status_codes=None,
        method="get",
    ):
        """Run a request with optional additional retries."""
        retries = max(0, int(retries if retries is not None else self.retries))
        timeout = timeout if timeout is not None else self.timeout
        last_error: BaseException | None = None

        if self.api_key and params is not None and "eutils.ncbi.nlm.nih.gov" in url:
            if isinstance(params, dict) and "api_key" not in params:
                params = {**params, "api_key": self.api_key}
            elif isinstance(params, (list, tuple)) and not any(
                p and p[0] == "api_key" for p in params
            ):
                params = list(params) + [("api_key", self.api_key)]

        is_ncbi_ebi = "ncbi.nlm.nih.gov" in url or "ebi.ac.uk" in url

        for attempt in range(retries + 1):
            last_attempt = attempt == retries
            try:
                response = requests.request(
                    method, url, params=params, data=data, timeout=timeout
                )
                if (
                    non_retryable_status_codes
                    and response.status_code in non_retryable_status_codes
                ):
                    return response

                # transient NCBI/EBI failure -> retry, then raise (never NULL)
                transient = None
                if is_ncbi_ebi and response.status_code in (429, 503):
                    transient = (RateLimitError, "rate limited")
                elif is_ncbi_ebi and response.status_code == 200:
                    body = response.text[:600].lower()
                    if "rate limit" in body or "too many requests" in body:
                        transient = (RateLimitError, "rate limited")
                elif is_ncbi_ebi and response.status_code >= 500:
                    transient = (ServerError, "server error")
                if transient:
                    exc, label = transient
                    if last_attempt:
                        raise exc(f"{label} (HTTP {response.status_code}) for {url}")
                    time.sleep(self.sleep_time * (2**attempt))
                    continue

                response.raise_for_status()
                return response
            except requests.RequestException as e:
                last_error = e
                status = getattr(getattr(e, "response", None), "status_code", None)
                if last_attempt:
                    # 429/503/5xx/network -> transient (raise); 4xx -> real error
                    if is_ncbi_ebi and (
                        status is None or status in (429, 503) or status >= 500
                    ):
                        if status in (429, 503):
                            raise RateLimitError(str(e)) from e
                        raise ServerError(str(e)) from e
                    raise last_error
                time.sleep(self.sleep_time * (2**attempt))

    def pmid_to_pmc(self, pmids):
        """Convert PMID(s) to PMC ID(s)

        Parameters
        ----------
        pmids: list or str
              PMID(s)

        Returns
        -------
        pmid_pmc_mapping: dict
                         Mapping of PMID to PMC ID
        """
        if isinstance(pmids, str):
            pmids = [pmids]

        pmid_pmc_mapping = {}

        for pmid in pmids:
            try:
                summary_url = self.base_url["esummary"]
                summary_params = {
                    "db": "pubmed",
                    "id": pmid,
                    "retmode": "json",
                }

                response = self._send_retryable_request(summary_url, summary_params)
                result = response.json()

                # Extract PMC ID from articleids
                if str(pmid) in result.get("result", {}):
                    article = result["result"][str(pmid)]
                    articleids = article.get("articleids", [])

                    for aid in articleids:
                        if aid.get("idtype") == "pmc":
                            pmc_id = aid.get("value")
                            pmid_pmc_mapping[pmid] = pmc_id
                            break

                time.sleep(self.sleep_time)

            except Exception as e:
                warnings.warn(f"Failed to get PMC ID for PMID {pmid}: {e}")
                pmid_pmc_mapping[pmid] = None

        return pmid_pmc_mapping

    def fetch_pmc_fulltext(self, pmc_id, retries=3):
        """Fetch full text from PMC article

        Parameters
        ----------
        pmc_id: str
               PMC ID (can be with or without 'PMC' prefix)
        retries: int
               Number of additional retries for failed PMC requests.
               Default: 3

        Returns
        -------
        fulltext: str
                 Full text of the article, or None if unavailable
        """
        # Ensure PMC ID has the PMC prefix
        if not pmc_id.startswith("PMC"):
            pmc_id = f"PMC{pmc_id}"

        try:
            fetch_url = self.base_url["efetch"]
            fetch_params = {"db": "pmc", "id": pmc_id, "retmode": "xml"}

            response = self._send_retryable_request(
                fetch_url, fetch_params, retries=retries
            )

            time.sleep(self.sleep_time)
            return response.text

        except Exception as e:
            warnings.warn(f"Failed to fetch full text for {pmc_id}: {e}")
            return None

    def extract_identifiers_from_text(self, text):
        """Extract GSE, PRJNA, SRP, and other identifiers from text

        Parameters
        ----------
        text: str
             Text to search for identifiers

        Returns
        -------
        identifiers: dict
                    Dictionary with lists of found identifiers by type
        """
        if not text:
            return {
                "gse": [],
                "prjna": [],
                "srp": [],
                "srr": [],
                "srx": [],
                "srs": [],
            }

        # Define patterns for different identifier types
        patterns = {
            "gse": r"GSE\d+",
            "prjna": r"PRJNA\d+",
            "srp": r"SRP\d+",
            "srr": r"SRR\d+",
            "srx": r"SRX\d+",
            "srs": r"SRS\d+",
        }

        identifiers = {}
        for id_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Convert to uppercase and remove duplicates
            identifiers[id_type] = sorted(list(set([m.upper() for m in matches])))

        return identifiers

    def pmc_to_identifiers(self, pmc_ids, convert_missing=True):
        """Extract database identifiers from PMC articles

        Parameters
        ----------
        pmc_ids: list or str
                PMC ID(s) (can be with or without 'PMC' prefix)
        convert_missing: bool
                        If True, automatically convert GSE↔SRP when one is found but not the other
                        Default: True

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with PMC IDs and extracted identifiers
        """
        if isinstance(pmc_ids, str):
            pmc_ids = [pmc_ids]

        results = []

        for pmc_id in pmc_ids:
            # Fetch full text
            fulltext = self.fetch_pmc_fulltext(pmc_id)

            if fulltext:
                # Extract identifiers
                identifiers = self.extract_identifiers_from_text(fulltext)

                if convert_missing:
                    # If we found GSE IDs but no SRP IDs, convert GSE to SRP
                    if identifiers["gse"] and not identifiers["srp"]:
                        try:
                            for gse_id in identifiers["gse"]:
                                gse_srp_df = self.gse_to_srp(gse_id)
                                if (
                                    not gse_srp_df.empty
                                    and "study_accession" in gse_srp_df.columns
                                ):
                                    srp_values = (
                                        gse_srp_df["study_accession"].dropna().tolist()
                                    )
                                    identifiers["srp"].extend(
                                        [str(x) for x in srp_values if not pd.isna(x)]
                                    )
                            identifiers["srp"] = sorted(list(set(identifiers["srp"])))
                            time.sleep(self.sleep_time)
                        except Exception:
                            pass

                    # If we found SRP IDs but no GSE IDs, convert SRP to GSE
                    elif identifiers["srp"] and not identifiers["gse"]:
                        try:
                            for srp_id in identifiers["srp"]:
                                srp_gse_df = self.srp_to_gse(srp_id)
                                if (
                                    not srp_gse_df.empty
                                    and "study_alias" in srp_gse_df.columns
                                ):
                                    gse_values = (
                                        srp_gse_df["study_alias"].dropna().tolist()
                                    )
                                    identifiers["gse"].extend(
                                        [str(x) for x in gse_values if not pd.isna(x)]
                                    )
                            identifiers["gse"] = sorted(
                                list(set(identifiers["gse"]))
                            )  # Remove duplicates
                            time.sleep(self.sleep_time)
                        except Exception:
                            pass  # If conversion fails, just keep what we found

                # Extract PRJNA from SRP metadata if we have SRP IDs
                if identifiers["srp"] and not identifiers["prjna"]:
                    try:
                        for srp_id in identifiers["srp"]:
                            srp_metadata = self.sra_metadata(srp_id)
                            if srp_metadata is not None and not srp_metadata.empty:
                                if "bioproject" in srp_metadata.columns:
                                    bioproject_values = (
                                        srp_metadata["bioproject"]
                                        .dropna()
                                        .unique()
                                        .tolist()
                                    )
                                    identifiers["prjna"].extend(
                                        [
                                            str(x)
                                            for x in bioproject_values
                                            if not pd.isna(x)
                                        ]
                                    )
                        identifiers["prjna"] = sorted(list(set(identifiers["prjna"])))
                        time.sleep(self.sleep_time)
                    except Exception:
                        pass

                results.append(
                    {
                        "pmc_id": (
                            pmc_id if pmc_id.startswith("PMC") else f"PMC{pmc_id}"
                        ),
                        "gse_ids": (
                            ",".join(identifiers["gse"])
                            if identifiers["gse"]
                            else pd.NA
                        ),
                        "prjna_ids": (
                            ",".join(identifiers["prjna"])
                            if identifiers["prjna"]
                            else pd.NA
                        ),
                        "srp_ids": (
                            ",".join(identifiers["srp"])
                            if identifiers["srp"]
                            else pd.NA
                        ),
                        "srr_ids": (
                            ",".join(identifiers["srr"])
                            if identifiers["srr"]
                            else pd.NA
                        ),
                        "srx_ids": (
                            ",".join(identifiers["srx"])
                            if identifiers["srx"]
                            else pd.NA
                        ),
                        "srs_ids": (
                            ",".join(identifiers["srs"])
                            if identifiers["srs"]
                            else pd.NA
                        ),
                    }
                )
            else:
                results.append(
                    {
                        "pmc_id": (
                            pmc_id if pmc_id.startswith("PMC") else f"PMC{pmc_id}"
                        ),
                        "gse_ids": pd.NA,
                        "prjna_ids": pd.NA,
                        "srp_ids": pd.NA,
                        "srr_ids": pd.NA,
                        "srx_ids": pd.NA,
                        "srs_ids": pd.NA,
                    }
                )

        return pd.DataFrame(results)

    def pmid_to_identifiers(self, pmids):
        """Extract database identifiers from PubMed articles via PMC

        Parameters
        ----------
        pmids: list or str
              PMID(s)

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with PMIDs, PMC IDs, and extracted identifiers
        """
        if isinstance(pmids, str):
            pmids = [pmids]

        # First convert PMIDs to PMC IDs
        pmid_pmc_mapping = self.pmid_to_pmc(pmids)

        results = []

        for pmid, pmc_id in pmid_pmc_mapping.items():
            if pmc_id:
                # Get identifiers from PMC
                pmc_results = self.pmc_to_identifiers([pmc_id])

                if not pmc_results.empty:
                    result = pmc_results.iloc[0].to_dict()
                    result["pmid"] = pmid
                    # Reorder columns to have pmid first
                    result = {
                        "pmid": result["pmid"],
                        "pmc_id": result["pmc_id"],
                        "gse_ids": result["gse_ids"],
                        "prjna_ids": result["prjna_ids"],
                        "srp_ids": result["srp_ids"],
                        "srr_ids": result["srr_ids"],
                        "srx_ids": result["srx_ids"],
                        "srs_ids": result["srs_ids"],
                    }
                    results.append(result)
                else:
                    results.append(
                        {
                            "pmid": pmid,
                            "pmc_id": pmc_id,
                            "gse_ids": pd.NA,
                            "prjna_ids": pd.NA,
                            "srp_ids": pd.NA,
                            "srr_ids": pd.NA,
                            "srx_ids": pd.NA,
                            "srs_ids": pd.NA,
                        }
                    )
            else:
                # No PMC ID available
                results.append(
                    {
                        "pmid": pmid,
                        "pmc_id": pd.NA,
                        "gse_ids": pd.NA,
                        "prjna_ids": pd.NA,
                        "srp_ids": pd.NA,
                        "srr_ids": pd.NA,
                        "srx_ids": pd.NA,
                        "srs_ids": pd.NA,
                    }
                )

        return pd.DataFrame(results)

    def pmid_to_gse(self, pmids):
        """Get GSE identifiers from PMID(s)

        Parameters
        ----------
        pmids: list or str
              PMID(s)

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with PMIDs and GSE identifiers
        """
        full_results = self.pmid_to_identifiers(pmids)
        return full_results[["pmid", "pmc_id", "gse_ids"]]

    def pmid_to_srp(self, pmids):
        """Get SRP identifiers from PMID(s)

        Parameters
        ----------
        pmids: list or str
              PMID(s)

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with PMIDs and SRP identifiers
        """
        full_results = self.pmid_to_identifiers(pmids)
        return full_results[["pmid", "pmc_id", "srp_ids"]]

    def doi_to_identifiers(self, dois):
        """Extract database identifiers from articles via DOI

        Parameters
        ----------
        dois: list or str
             DOI(s)

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with DOIs, PMIDs, PMC IDs, and extracted identifiers
        """
        if isinstance(dois, str):
            dois = [dois]

        doi_pmid_mapping = self.doi_to_pmid(dois)

        results = []

        for doi, pmid in doi_pmid_mapping.items():
            if pmid:
                pmid_results = self.pmid_to_identifiers([pmid])

                if not pmid_results.empty:
                    result = pmid_results.iloc[0].to_dict()
                    result["doi"] = doi
                    result = {
                        "doi": result["doi"],
                        "pmid": result["pmid"],
                        "pmc_id": result["pmc_id"],
                        "gse_ids": result["gse_ids"],
                        "prjna_ids": result["prjna_ids"],
                        "srp_ids": result["srp_ids"],
                        "srr_ids": result["srr_ids"],
                        "srx_ids": result["srx_ids"],
                        "srs_ids": result["srs_ids"],
                    }
                    results.append(result)
                else:
                    results.append(
                        {
                            "doi": doi,
                            "pmid": pmid,
                            "pmc_id": pd.NA,
                            "gse_ids": pd.NA,
                            "prjna_ids": pd.NA,
                            "srp_ids": pd.NA,
                            "srr_ids": pd.NA,
                            "srx_ids": pd.NA,
                            "srs_ids": pd.NA,
                        }
                    )
            else:
                # No PMID available
                results.append(
                    {
                        "doi": doi,
                        "pmid": pd.NA,
                        "pmc_id": pd.NA,
                        "gse_ids": pd.NA,
                        "prjna_ids": pd.NA,
                        "srp_ids": pd.NA,
                        "srr_ids": pd.NA,
                        "srx_ids": pd.NA,
                        "srs_ids": pd.NA,
                    }
                )

        return pd.DataFrame(results)

    def doi_to_gse(self, dois):
        """Get GSE identifiers from DOI(s)

        Parameters
        ----------
        dois: list or str
             DOI(s)

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with DOIs and GSE identifiers
        """
        full_results = self.doi_to_identifiers(dois)
        return full_results[["doi", "pmid", "pmc_id", "gse_ids"]]

    def doi_to_srp(self, dois):
        """Get SRP identifiers from DOI(s)

        Parameters
        ----------
        dois: list or str
             DOI(s)

        Returns
        -------
        results_df: pandas.DataFrame
                   DataFrame with DOIs and SRP identifiers
        """
        full_results = self.doi_to_identifiers(dois)
        return full_results[["doi", "pmid", "pmc_id", "srp_ids"]]

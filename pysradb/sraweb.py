"""Utilities to interact with SRA online"""

import concurrent.futures
import os
import pandas as pd
import sys
import time
import warnings
from collections import OrderedDict
from json.decoder import JSONDecodeError
from xml.parsers.expat import ExpatError

import numpy as np
import pandas as pd
import requests
import xmltodict

from .sradb import SRAdb

warnings.simplefilter(action="ignore", category=FutureWarning)

from xml.sax.saxutils import escape


def xmlescape(data):
    return escape(data, entities={"'": "&apos;", '"': "&quot;"})


def _order_first(df, column_order_list):
    columns = column_order_list + [
        col for col in df.columns.tolist() if col not in column_order_list
    ]
    # check if all columns do exist in the dataframe
    if len(set(columns).intersection(df.columns)) == len(columns):
        df = df.loc[:, columns]
    df = df.mask(df.applymap(str).eq("[]"))
    df = df.fillna(pd.NA)
    return df


def _retry_response(base_url, payload, key, max_retries=10):
    """Rerty fetching esummary if API rate limit exceeeds"""
    for index, _ in enumerate(range(max_retries)):
        try:
            request = requests.get(base_url, params=OrderedDict(payload))
            response = request.json()
            results = response[key]
            return response
        except KeyError:
            # sleep for increasing times
            time.sleep(index + 1)
            continue
    raise RuntimeError("Failed to fetch esummary. API rate limit exceeded.")


def get_retmax(n_records, retmax=500):
    """Get retstart and retmax till n_records are exhausted"""
    for i in range(0, n_records, retmax):
        yield i


class SRAweb(SRAdb):
    def __init__(self, api_key=None):
        """
        Initialize a SRAwebdb.

        Parameters
        ----------

        api_key: string
                 API key for ncbi eutils.
        """
        self.base_url = dict()
        self.base_url[
            "esummary"
        ] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        self.base_url[
            "esearch"
        ] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_url[
            "efetch"
        ] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        self.ena_fastq_search_url = "https://www.ebi.ac.uk/ena/portal/api/filereport"
        self.ena_params = [("result", "read_run"), ("fields", "fastq_ftp")]

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

        if api_key is not None:
            self.esearch_params["sra"].append(("api_key", str(api_key)))
            self.esearch_params["geo"].append(("api_key", str(api_key)))
            self.efetch_params.append(("api_key", str(api_key)))
            self.sleep_time = 1 / 10
        else:
            self.sleep_time = 1 / 3

    @staticmethod
    def format_xml(string):
        """Create a fake root to make 'string' a valid xml

        Parameters
        ----------
        string: str

        Returns
        --------
        xml: str
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
                xml, process_namespaces=True, dict_constructor=OrderedDict
            )
            json = xmldict["root"]
        except ExpatError:
            raise RuntimeError("Unable to parse xml: {}".format(xml))
        return json

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
        request = requests.get(self.ena_fastq_search_url, params=OrderedDict(payload))
        request_text = request.text.strip()
        urls = []
        for line in request_text.split("\n"):
            if "fastq_ftp" in line:
                continue
            line = line.strip()
            line_split = line.split("\t")
            if len(line_split) != 2:
                continue
            srr, url = line.split("\t")
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
            return pd.DataFrame(
                urls_expanded,
                columns=[
                    "run_accession",
                    "ena_fastq_http_1",
                    "ena_fastq_http_2",
                    "ena_fastq_ftp_1",
                    "ena_fastq_ftp_2",
                ],
            ).sort_values(by="run_accession")
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
        request = requests.post(self.base_url["esearch"], data=OrderedDict(payload))
        try:
            esearch_response = request.json()
        except JSONDecodeError:
            sys.stderr.write(
                "Unable to parse esummary response json: {}{}. Will retry once.".format(
                    request.text, os.linesep
                )
            )
            retry_after = request.headers.get("Retry-After", 1)
            time.sleep(int(retry_after))
            request = requests.post(self.base_url["esearch"], data=OrderedDict(payload))
            try:
                esearch_response = request.json()
            except JSONDecodeError:
                sys.stderr.write(
                    "Unable to parse esummary response json: {}{}. Aborting.".format(
                        request.text, os.linesep
                    )
                )
                sys.exit(1)

            # retry again

        if "esummaryresult" in esearch_response:
            print("No result found")
            return
        if "error" in esearch_response:
            # API rate limite exceeded
            esearch_response = _retry_response(
                self.base_url["esearch"], payload, "esearchresult"
            )

        n_records = int(esearch_response["esearchresult"]["count"])

        results = {}
        for retstart in get_retmax(n_records):
            payload = self.esearch_params[db].copy()
            payload += self.create_esummary_params(esearch_response["esearchresult"])
            payload = OrderedDict(payload)
            payload["retstart"] = retstart
            request = requests.get(
                self.base_url["esummary"], params=OrderedDict(payload)
            )
            try:
                response = request.json()
            except JSONDecodeError:
                time.sleep(1)
                response = _retry_response(self.base_url["esummary"], payload, "result")

            if "error" in response:
                # API rate limite exceeded
                response = _retry_response(self.base_url["esummary"], payload, "result")
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

        request = requests.get(self.base_url["esearch"], params=OrderedDict(payload))
        esearch_response = request.json()
        if "esummaryresult" in esearch_response:
            print("No result found")
            return
        if "error" in esearch_response:
            # API rate limite exceeded
            esearch_response = _retry_response(
                self.base_url["esearch"], payload, "esearchresult"
            )

        n_records = int(esearch_response["esearchresult"]["count"])

        results = {}
        for retstart in get_retmax(n_records):
            payload = self.efetch_params.copy()
            payload += self.create_esummary_params(esearch_response["esearchresult"])
            payload = OrderedDict(payload)
            payload["retstart"] = retstart
            request = requests.get(self.base_url["efetch"], params=OrderedDict(payload))
            request_text = request.text.strip()
            try:
                request_json = request.json()
            except:
                request_json = {}  # eval(request_text)

            if "error" in request_json:
                # print("Encountered: {}".format(request_json))
                # print("Headers: {}".format(request.headers))
                # Handle API-rate limit exceeding
                try:
                    retry_after = request.headers["Retry-After"]
                except KeyError:
                    if request_json["error"] == "error forwarding request":
                        sys.stderr.write("Encountered error while making request.\n")
                        sys.exit(1)
                time.sleep(int(retry_after))
                # try again
                request = requests.get(
                    self.base_url["efetch"], params=OrderedDict(payload)
                )
                request_text = request.text.strip()
                try:
                    request_json = request.json()
                    if request_json["error"] == "error forwarding request":
                        sys.stderr.write("Encountered error while making request.\n")
                        return
                except:
                    request_json = {}  # eval(request_text)
            try:
                xml_response = xmltodict.parse(
                    request_text, dict_constructor=OrderedDict
                )

                exp_response = xml_response.get("EXPERIMENT_PACKAGE_SET", {})
                response = exp_response.get("EXPERIMENT_PACKAGE", {})
            except ExpatError:
                sys.stderr.write(
                    "Unable to parse xml: {}{}".format(request_text, os.linesep)
                )
                sys.exit(1)
            if not response:
                sys.stderr.write(
                    "Unable to parse xml response. Received: {}{}".format(
                        xml_response, os.linesep
                    )
                )
                sys.exit(1)
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
        **kwargs
    ):
        esummary_result = self.get_esummary_response("sra", srp)
        try:
            uids = esummary_result["uids"]
        except KeyError:
            print("No results found for {}".format(srp))
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
        metadata_df = pd.DataFrame(sra_record).drop_duplicates()
        if "run_accession" in metadata_df.columns:
            metadata_df = metadata_df.sort_values(by="run_accession")
        metadata_df.columns = [x.lower().strip() for x in metadata_df.columns]
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
                        value = value_x["VALUE"]
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
        if "run_accession" in metadata_df.columns:
            return metadata_df.sort_values(by="run_accession")
        return metadata_df

    def fetch_gds_results(self, gse, **kwargs):
        result = self.get_esummary_response("geo", gse)

        try:
            uids = result["uids"]
        except KeyError:
            print("No results found for {} | Obtained result: {}".format(gse, result))
            return None
        gse_records = []
        for uid in uids:
            record = result[uid]
            del record["uid"]
            if record["extrelations"]:
                extrelations = record["extrelations"]
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
        if not len(gse_records):
            print("No results found for {}".format(gse))
            return None
        return pd.DataFrame(gse_records)

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
        gse_df = self.fetch_gds_results(gse, **kwargs)
        gse_df = gse_df.rename(
            columns={"accession": "study_alias", "SRA": "study_accession"}
        )
        gse_df_subset = None
        if "GSE" in gse_df.entrytype.unique():
            gse_df_subset = gse_df[gse_df.entrytype == "GSE"]
            common_gses = set(gse_df.study_alias.unique()).intersection(gse)
            if len(common_gses) < len(gse):
                gse_df_subset = None
        if gse_df_subset is None:
            # sometimes SRX ids ar ereturned instead of an entire project
            # see https://github.com/saketkc/pysradb/issues/186
            # GSE: GSE209835; SRP =SRP388275
            gse_df_subset_gse = gse_df[gse_df.entrytype == "GSE"]
            gse_of_interest = list(set(gse).difference(gse_df.study_alias.unique()))
            gse_df_subset_other = gse_df[gse_df.entrytype != "GSE"]
            srx = gse_df_subset_other.study_accession.tolist()
            srp_df = self.srx_to_srp(srx)
            srp_unique = list(
                set(srp_df.study_accession.unique()).difference(
                    gse_df_subset_gse.study_accession.tolist()
                )
            )
            new_gse_df = pd.DataFrame(
                {"study_alias": gse_of_interest, "study_accession": srp_unique}
            )
            gse_df_subset = pd.concat([gse_df_subset_gse, new_gse_df])
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
        gsm_df = self.fetch_gds_results(gsm, **kwargs)
        gsm_df = gsm_df[gsm_df.entrytype == "GSE"]
        gsm_df = gsm_df.rename(
            columns={"accession": "study_alias", "SRA": "study_accession"}
        )
        return gsm_df[["study_alias", "study_accession"]]

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

    def search(self, *args, **kwargs):
        raise NotImplementedError("Search not yet implemented for Web")

    def close(self):
        # Dummy method to mimick SRAdb() object
        # TODO: fix this
        pass

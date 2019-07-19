from collections import OrderedDict
from html import unescape

import pandas as pd
import re
import sys
import time

import requests
import xmltodict

from .sradb import SRAdb


def get_retmax(n_records, retmax=500):
    """Get retstart and retmax till n_records are exhausted"""
    for i in range(0, n_records, retmax):
        yield i


class SRAweb(SRAdb):
    def __init__(self):
        self.base_url = {}
        self.base_url[
            "esummary"
        ] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        self.base_url[
            "esearch"
        ] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.esearch_params = {}
        self.esearch_params["sra"] = [
            ("db", "sra"),
            ("usehistory", "y"),
            ("retmode", "json"),
        ]
        self.esearch_params["geo"] = [
            ("db", "gds"),
            ("usehistory", "y"),
            ("retmode", "json"),
        ]

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
        string = unescape(string.strip())
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
        return xmltodict.parse(xml)["root"]

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

        request = requests.get(self.base_url["esearch"], params=OrderedDict(payload))
        esearch_response = request.json()
        # print(response)
        if "esummaryresult" in esearch_response:
            print("No result found")
            return

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
            response = request.json()
            if retstart == 0:
                results = response["result"]
            else:
                result = response["result"]
                for key, value in result.items():
                    if key in list(results.keys()):
                        results[key] += value
                    else:
                        results[key] = value
            time.sleep(0.1)
        return results

        # print(response)
        if "esummaryresult" in list(response.keys()):
            print("No result found")
            return

        return response["result"]

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
            sys.exit(1)
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
            runs = run_json["Run"]
            if not isinstance(runs, list):
                runs = [runs]
            exp_title = exp_json["Summary"]["Title"]
            exp_platform = exp_json["Summary"]["Platform"]
            exp_total_runs = exp_json["Summary"]["Statistics"]["@total_runs"]
            exp_total_total_spots = exp_json["Summary"]["Statistics"]["@total_spots"]
            exp_total_total_size = exp_json["Summary"]["Statistics"]["@total_size"]

            # experiment_accession
            exp_ID = exp_json["Experiment"]["@acc"]
            # experiment_title
            exp_name = exp_json["Experiment"]["@name"]

            exp_organism = exp_json["Organism"]
            # organism_name
            try:
                exp_organism_name = exp_organism["@ScientificName"]
            except:
                exp_organism_name = ""

            # taxid
            exp_taxid = exp_organism["@taxid"]

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
            # library_layout
            exp_library_layout = list(exp_library_descriptor["LIBRARY_LAYOUT"].keys())[
                0
            ]

            experiment_record = OrderedDict()
            experiment_record["experiment_accession"] = exp_ID
            experiment_record["experiment_title"] = exp_name
            experiment_record["experiment_desc"] = exp_title

            experiment_record["organism_taxid "] = exp_taxid
            experiment_record["organism_name"] = exp_organism_name

            experiment_record["library_strategy"] = exp_library_strategy
            experiment_record["library_source"] = exp_library_source
            experiment_record["library_selection"] = exp_library_selection
            experiment_record["library_source"] = exp_library_source

            experiment_record["sample_accession"] = exp_sample_ID
            experiment_record["sample_title"] = exp_sample_name

            experiment_record["study_accession"] = exp_json["Study"]["@acc"]

            for run_record in runs:
                run_accession = run_record["@acc"]
                run_total_spots = run_record["@total_spots"]
                run_total_bases = run_record["@total_bases"]

                experiment_record["run_accession"] = run_accession
                experiment_record["run_total_spots"] = run_total_spots
                experiment_record["run_total_bases"] = run_total_bases

                sra_record.append(experiment_record)
        return pd.DataFrame(sra_record)

    def fetch_gds_results(self, gse, **kwargs):
        result = self.get_esummary_response("geo", gse)

        try:
            uids = result["uids"]
        except KeyError:
            print("No results found for {}".format(gse))
            sys.exit(1)
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
            sys.exit(1)
        return pd.DataFrame(gse_records)

    def gse_to_gsm(self, gse, **kwargs):
        gse_df = self.fetch_gds_results(gse)
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
        for index, row in gse_df.iterrows():
            if row.entrytype == "GSE":
                study_alias = row["experiment_accession"]
            # If GSM is ecnountered, apply it the
            # previously encountered GSE
            elif row.entrytype == "GSM":
                gse_df.loc[index, "study_alias"] = study_alias
        gse_df = gse_df[gse_df.entrytype == "GSM"]
        if kwargs["detailed"] == True:
            return gse_df
        return gse_df[
            ["study_alias", "experiment_alias", "experiment_accession"]
        ].drop_duplicates()

    def gse_to_srp(self, gse, **kwargs):
        gse_df = self.fetch_gds_results(gse)
        gse_df = gse_df[gse_df.entrytype == "GSE"]
        gse_df = gse_df.rename(
            columns={"accession": "study_alias", "SRA": "study_accession"}
        )
        return gse_df[["study_alias", "study_accession"]].drop_duplicates()

    def gsm_to_srp(self, gsm, **kwargs):
        gsm_df = self.fetch_gds_results(gsm)
        gsm_df = gsm_df[gsm_df.entrytype == "GSE"]
        gsm_df = gsm_df.rename(
            columns={"accession": "experiment_alias", "SRA": "study_accession"}
        )
        return gsm_df[["experiment_alias", "study_accession"]].drop_duplicates()

    def gsm_to_srr(self, gsm, **kwargs):
        gsm_df = self.fetch_gds_results(gsm)
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
        gsm_df = self.fetch_gds_results(gsm)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"].rename(
            columns={"SRA": "experiment_accession", "accession": "experiment_alias"}
        )
        srx = gsm_df.experiment_accession.tolist()
        time.sleep(0.3)
        srs_df = self.srx_to_srs(srx)
        gsm_df = srs_df.merge(gsm_df, on="experiment_accession")[
            ["experiment_alias", "sample_accession"]
        ]
        return gsm_df.drop_duplicates()

    def gsm_to_srx(self, gsm, **kwargs):
        """Get SRX for a GSM"""
        gsm_df = self.fetch_gds_results(gsm)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"].rename(
            columns={"SRA": "experiment_accession", "accession": "experiment_alias"}
        )
        return gsm_df[["experiment_alias", "experiment_accession"]].drop_duplicates()

    def srp_to_gse(self, srp, **kwargs):
        """Get GSE for a SRP"""
        srp_df = self.fetch_gds_results(srp)
        srp_df = srp_df[srp_df.entrytype == "GSE"]
        srp_df = srp_df.rename(
            columns={"accession": "study_alias", "SRA": "study_accession"}
        )
        return srp_df[["study_accession", "study_alias"]].drop_duplicates()

    def srp_to_srr(self, srp, **kwargs):
        """Get SRR for a SRP"""
        srp_df = self.sra_metadata(srp)
        return srp_df[["study_accession", "run_accession"]].drop_duplicates()

    def srp_to_srs(self, srp, **kwargs):
        """Get SRS for a SRP"""
        srp_df = self.sra_metadata(srp)
        return srp_df[["study_accession", "sample_accession"]].drop_duplicates()

    def srp_to_srx(self, srp, **kwargs):
        """Get SRX for a SRP"""
        srp_df = self.sra_metadata(srp)
        srp_df["study_accesssion"] = srp
        return srp_df[["study_accession", "experiment_accession"]].drop_duplicates()

    def srr_to_gsm(self, srr, **kwargs):
        """Get GSM for a SRR"""
        srr_df = self.srr_to_srp(srr, detailed=True)
        srp = srr_df.study_accession.tolist()
        gse_df = self.fetch_gds_results(srp)
        gse_df = gse_df[gse_df.entrytype == "GSE"].rename(
            columns={"SRA": "project_accession", "accession": "project_alias"}
        )
        gsm_df = self.gse_to_gsm(gse_df.project_alias.tolist(), detailed=True)
        joined_df = gsm_df.merge(srr_df, on="experiment_accession")
        return joined_df[["run_accession", "experiment_alias"]].drop_duplicates()

    def srr_to_srp(self, srr, **kwargs):
        """Get SRP for a SRR"""
        srr_df = self.sra_metadata(srr)
        if kwargs["detailed"] == True:
            return srr_df
        return srr_df[["run_accession", "study_accession"]].drop_duplicates()

    def srr_to_srs(self, srr, **kwargs):
        """Get SRS for a SRR"""
        srr_df = self.sra_metadata(srr)
        return srr_df[["run_accession", "sample_accession"]].drop_duplicates()

    def srr_to_srx(self, srr, **kwargs):
        """Get SRX for a SRR"""
        srr_df = self.sra_metadata(srr)
        return srr_df[["run_accession", "experiment_accession"]].drop_duplicates()

    def srs_to_gsm(self, srs, **kwargs):
        """Get GSM for a SRS"""
        srx_df = self.srs_to_srx(srs)
        time.sleep(0.5)
        gsm_df = self.srx_to_gsm(srx_df.experiment_accession.tolist())
        srs_df = srx_df.merge(gsm_df, on="experiment_accession")
        return srs_df[["sample_accession", "experiment_alias"]]

    def srx_to_gsm(self, srx, **kwargs):
        gsm_df = self.fetch_gds_results(srx)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"].rename(
            columns={"SRA": "experiment_accession", "accession": "experiment_alias"}
        )
        return gsm_df[["experiment_accession", "experiment_alias"]]

    def srs_to_srx(self, srs, **kwargs):
        """Get SRX for a SRS"""
        srs_df = self.sra_metadata(srs)
        return srs_df[["sample_accession", "experiment_accession"]]

    def srx_to_srp(self, srx, **kwargs):
        """Get SRP for a SRX"""
        srx_df = self.sra_metadata(srx)
        return srx_df[["experiment_accession", "study_accession"]]

    def srx_to_srr(self, srx, **kwargs):
        """Get SRR for a SRX"""
        srx_df = self.sra_metadata(srx)
        return srx_df[["experiment_accession", "run_accession"]]

    def srx_to_srs(self, srx, **kwargs):
        """Get SRS for a SRX"""
        srx_df = self.sra_metadata(srx)
        return srx_df[["experiment_accession", "sample_accession"]]

    def search(self, *args, **kwargs):
        raise NotImplementedError("Search not yet implemented for Web")

    def close(self):
        # Dummy method to mimick SRAdb() object
        # TODO: fix this
        pass

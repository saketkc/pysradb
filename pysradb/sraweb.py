from collections import OrderedDict

import pandas as pd
import requests


class SRAweb(object):
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

    @classmethod
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

    @classmethod
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
        retmax = esearchresult["retmax"]
        return [
            ("query_key", query_key),
            ("WebEnv", webenv),
            ("retstart", retstart),
            ("retmax", retmax),
        ]

    def get_esummary_reponse(self, db, term):

        assert db in ["sra", "geo"]

        payload = self.esearch_params[db]
        payload += [("term", term)]
        request = requests.get(self.base_url["esearch"], params=OrderedDict(payload))
        response = request.json()
        if "esummaryresult" in response:
            print("No result found")
            return

        payload = self.esearch_params[db]
        payload += self.create_esummary_params(response["esearchresult"])
        request = requests.get(self.base_url["esummary"], params=OrderedDict(payload))

        response = request.json()

        if "esummaryresult" in response:
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
    ):

        esummary_result = self.get_esummary_reponse("sra", srp)
        uids = esummary_result["uids"]
        exps_xml = OrderedDict()
        runs_xml = OrderedDict()

        exps_json = OrderedDict()
        runs_json = OrderedDict()

        for uid in uids:
            exps_xml[uid] = format_xml(esummary_result[uid]["expxml"])
            runs_xml[uid] = format_xml(esummary_result[uid]["runs"])

        for uid in uids:
            exps_json[uid] = xml_to_json(exps_xml[uid])
            runs_json[uid] = xml_to_json(runs_xml[uid])

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
            exp_organism_name = exp_organism["@ScientificName"]
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

            experiment_record["project_accession"] = srp

            for run_record in runs:
                run_accession = run_record["@acc"]
                run_total_spots = run_record["@total_spots"]
                run_total_bases = run_record["@total_bases"]

                experiment_record["run_accession"] = run_accession
                experiment_record["run_total_spots"] = run_total_spots
                experiment_record["run_total_bases"] = run_total_bases

                sra_record.append(experiment_record)
        return pd.DataFrame(sra_record)

    def srp_to_gse(self, srp):
        esummary_result = self.get_esummary_reponse("geo", srp)
        if not esummary_result:
            return

        gse_records = []
        uids = esummary_result["uids"]
        for uid in uids:
            accession = esummary_result[uid]["accession"]
            title = esummary_result[uid]["title"]
            gse_records.append(
                {
                    "experiment_accession": accession,
                    "experiment_title": title,
                    "project_accession": srp,
                }
            )

        return pd.DataFrame(gse_records)

    def fetch_gds_results(self, gse):
        result = self.get_esummary_reponse("geo", gse)
        uids = result["uids"]
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
        return pd.DataFrame(gse_records)

    def gse_to_gsm(self, gse):
        gse_df = self.fetch_gds_results(gse)
        gse_df["project_alias"] = gse
        gse_df = gse_df[gse_df.entrytype == "GSM"]

        return gse_df.rename(
            columns={"accession": "experiment_alias", "SRA": "experiment_accession"}
        )[["project_alias", "experiment_alias"]]

    def gse_to_srp(self, gse):
        gse_df = self.fetch_gds_results(gse)
        gse_df = gse_df[gse_df.entrytype == "GSE"]
        return gse_df.rename(
            columns={"accession": "project_alias", "SRA": "project_accession"}
        )[["project_alias", "project_accession"]]

    def gsm_to_srp(self, gsm):
        gsm_df = self.fetch_gds_results(gsm)
        gsm_df = gsm_df[gsm_df.entrytype == "GSE"]
        return gsm_df.rename(
            columns={"accession": "experiment_alias", "SRA": "project_accession"}
        )[["experiment_alias", "project_accession"]]

    def gsm_to_srr(self, gsm):
        gsm_df = self.fetch_gds_results(gsm)
        gsm_df = gsm_df[gsm_df.entrytype == "GSM"]
        return gsm_df

    def gsm_to_srs(self, gsm):
        """Get SRS for a GSM"""
        pass

    def gsm_to_srx(self, gsm):
        """Get SRX for a GSM"""
        pass

    def srp_to_gse(self, srp):
        """Get GSE for a SRP"""
        pass

    def srp_to_srr(self, srp):
        """Get SRR for a SRP"""
        pass

    def srp_to_srs(self, srp):
        """Get SRS for a SRP"""
        pass

    def srp_to_srx(self, srp):
        """Get SRX for a SRP"""
        srp_df = self.sra_metadata(srp)
        srp_df["project_accesssion"] = srp
        return srp_df

    def srr_to_gsm(self, srr):
        """Get GSM for a SRR"""
        pass

    def srr_to_srp(self, srr):
        """Get SRP for a SRR"""
        pass

    def srr_to_srs(self, srr):
        """Get SRS for a SRR"""
        pass

    def srr_to_srx(self, srr):
        """Get SRX for a SRR"""
        pass

    def srs_to_gsm(self, srs):
        """Get GSM for a SRS"""
        pass

    def srs_to_srx(self, srs):
        """Get SRX for a SRS"""
        pass

    def srx_to_srp(self, srx):
        """Get SRP for a SRX"""
        pass

    def srx_to_srr(self, srx):
        """Get SRR for a SRX"""
        pass

    def srx_to_srs(self, srx):
        """Get SRS for a SRX"""

        pass
        # for record in

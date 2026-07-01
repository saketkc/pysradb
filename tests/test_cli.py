from pysradb import cli


def test_parse_args_dispatches_gse_to_gsm(monkeypatch):
    calls = []

    def fake_gse_to_gsm(gse_ids, saveto, detailed, desc, expand):
        calls.append((gse_ids, saveto, detailed, desc, expand))

    monkeypatch.setattr(cli, "gse_to_gsm", fake_gse_to_gsm)

    cli.parse_args(["gse-to-gsm", "GSE123"])

    assert calls == [(["GSE123"], None, False, False, False)]


def test_parse_args_dispatches_pmid_to_identifiers_retries(monkeypatch):
    calls = []

    def fake_pmid_to_identifiers(pmid_ids, saveto, retries, timeout):
        calls.append((pmid_ids, saveto, retries, timeout))

    monkeypatch.setattr(cli, "pmid_to_identifiers", fake_pmid_to_identifiers)

    cli.parse_args(["pmid-to-identifiers", "--retries", "2", "27373336"])

    assert calls == [(["27373336"], None, 2, 60)]


def test_parse_args_dispatches_pmid_to_identifiers_default_retries(monkeypatch):
    calls = []

    def fake_pmid_to_identifiers(pmid_ids, saveto, retries, timeout):
        calls.append((pmid_ids, saveto, retries, timeout))

    monkeypatch.setattr(cli, "pmid_to_identifiers", fake_pmid_to_identifiers)

    cli.parse_args(["pmid-to-identifiers", "27373336"])

    assert calls == [(["27373336"], None, 3, 60)]

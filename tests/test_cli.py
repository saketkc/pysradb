from pysradb import cli


def test_parse_args_dispatches_gse_to_gsm(monkeypatch):
    calls = []

    def fake_gse_to_gsm(gse_ids, saveto, detailed, desc, expand):
        calls.append((gse_ids, saveto, detailed, desc, expand))

    monkeypatch.setattr(cli, "gse_to_gsm", fake_gse_to_gsm)

    cli.parse_args(["gse-to-gsm", "GSE123"])

    assert calls == [(["GSE123"], None, False, False, False)]

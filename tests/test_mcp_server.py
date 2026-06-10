import pandas as pd
import pytest

from pysradb.mcp_server import (
    ACCESSION_CONVERSIONS,
    MCP_TOOL_NAMES,
    _limited_records,
    convert_accession,
    create_server,
    extract_identifiers_from_text,
    list_capabilities,
)


def test_limited_records_truncates_and_serializes_nulls():
    df = pd.DataFrame({"accession": ["SRR1", "SRR2"], "spots": [10, None]})

    result = _limited_records(df, limit=1)

    assert result["columns"] == ["accession", "spots"]
    assert result["records"] == [{"accession": "SRR1", "spots": 10.0}]
    assert result["returned"] == 1
    assert result["total_rows"] == 2
    assert result["truncated"] is True


def test_convert_accession_rejects_unsupported_pair():
    with pytest.raises(ValueError, match="Unsupported conversion"):
        convert_accession("SRR123", "doi")


def test_list_capabilities_advertises_all_mcp_tools():
    capabilities = list_capabilities()

    assert capabilities["tools"] == MCP_TOOL_NAMES
    assert capabilities["accession_conversions"] == sorted(ACCESSION_CONVERSIONS)
    assert "bulk_sra_download" in capabilities["omitted_by_design"]


def test_extract_identifiers_from_text_is_network_free():
    result = extract_identifiers_from_text("See GSE123, PRJNA456, SRP789, SRR101.")

    assert result["gse"] == ["GSE123"]
    assert result["prjna"] == ["PRJNA456"]
    assert result["srp"] == ["SRP789"]
    assert result["srr"] == ["SRR101"]


def test_create_server_registers_advertised_tools():
    pytest.importorskip("mcp")

    server = create_server()

    assert sorted(server._tool_manager._tools) == sorted(MCP_TOOL_NAMES)

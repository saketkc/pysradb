import subprocess
from pathlib import Path


def test_geo_matrix_download(tmp_path):
    accession = "GSE10072"
    out_dir = tmp_path / "should_be_out"

    result = subprocess.run(
        [
            "pysradb",
            "geo-matrix",
            "--accession",
            accession,
            "--to-tsv",
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
    )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    # Look in the actual output location used by the CLI
    expected_dir = out_dir / accession
    tsv_files = list(expected_dir.glob("*.tsv"))
    print("TSV files found in output location:", tsv_files)
    assert tsv_files, f"No TSV file found in output directory {expected_dir}"

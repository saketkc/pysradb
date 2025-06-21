# pysradb

## GEO Matrix File Download & Parsing

### Download and parse GEO matrix files from the command line

You can now fetch and convert GEO matrix files to TSV easily.

#### **If you are running from the source directory (where `cli.py` is located):**

From inside the `pysradb/pysradb` directory, use:

```powershell
python -m pysradb.cli geo-matrix --accession GSE12345 --to-tsv
```

#### **If you have installed `pysradb` as a package:**

From anywhere, you can use:

```bash
pysradb geo-matrix --accession GSE12345 --to-tsv
```

- Downloads matrix files for the given GEO accession (e.g., GSE12345)
- If `--to-tsv` is provided, parses the matrix file(s) to a tab-separated file, skipping metadata rows (starting with `!`).
- Use `--out-dir` to specify the output directory.

#### Example

```powershell
python -m pysradb.cli geo-matrix --accession GSE234190 --to-tsv --out-dir C:\tmp\geodata
```

or if installed:

```bash
pysradb geo-matrix --accession GSE234190 --to-tsv --out-dir /tmp/geodata
```

---

For more info, run:

```bash
pysradb geo-matrix --help
```
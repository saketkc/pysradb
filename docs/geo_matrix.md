# GEO Matrix File Support

pysradb now supports downloading and parsing GEO Matrix files, which contain processed expression data from NCBI's Gene Expression Omnibus (GEO).

## What are GEO Matrix Files?

GEO Matrix files are tab-delimited text files that contain processed expression data from microarray or sequencing experiments. They typically have the following structure:

1. Metadata lines that start with `!` character
2. A header line with sample identifiers
3. Data rows with gene/probe identifiers and expression values

## Command Line Usage

### Download GEO Matrix Files

To download matrix files for a GEO accession:

```bash
pysradb geo-matrix --accession GSE234190
```

### Download and Convert to TSV

To download matrix files and convert them to a clean TSV format:

```bash
pysradb geo-matrix --accession GSE234190 --to-tsv
```

### Specify Output Directory

```bash
pysradb geo-matrix --accession GSE234190 --out-dir ./my_data
```

### Specify Output TSV File

```bash
pysradb geo-matrix --accession GSE234190 --to-tsv --output-file ./my_data/expression_data.tsv
```

### Download Only Matrix Files with Existing Command

You can also use the existing `download` command with the new `--matrix-only` flag:

```bash
pysradb download --geo GSE234190 --matrix-only
```

## Python API Usage

### Basic Usage

```python
from pysradb.geomatrix import GEOMatrix

# Initialize with a GEO accession
matrix = GEOMatrix("GSE234190")

# Download matrix files
matrix.download_matrix(out_dir="./output")

# Parse matrix file to DataFrame
metadata, data = matrix.parse_matrix()

# Get just the DataFrame
df = matrix.to_dataframe()

# Export to TSV
matrix.to_tsv("output.tsv")
```

### Accessing Matrix Metadata

The metadata from the matrix file is stored as a dictionary:

```python
matrix = GEOMatrix("GSE234190")
matrix.download_matrix()
metadata, _ = matrix.parse_matrix()

# Print some metadata fields
print(metadata["Series_title"])
print(metadata["Series_summary"])
```

### Working with the Expression Data

The expression data is stored as a pandas DataFrame:

```python
matrix = GEOMatrix("GSE234190")
matrix.download_matrix()
df = matrix.to_dataframe()

# Basic DataFrame operations
print(df.shape)
print(df.head())

# Filter for specific genes
filtered_df = df[df.index.str.contains("BRCA1")]

# Calculate statistics
mean_expression = df.mean(axis=1)
```

## File Structure

GEO Matrix files typically have the following structure:

```
!Series_title	"Sample title"
!Series_summary	"Sample summary"
!Series_overall_design	"Overall design"
... (more metadata lines)
!series_matrix_table_begin
	GSM1	GSM2	GSM3
GENE1	0.5	0.7	0.2
GENE2	1.2	0.9	1.5
... (more data rows)
!series_matrix_table_end
```

The parser in pysradb handles this structure and separates the metadata from the data table.

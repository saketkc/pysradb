# Tasks for Implementing GEO Matrix File Support in pysradb

## Implementation Plan

### 1. Core Functionality Development

#### 1.1 Extend GEOweb Class
- [ ] Add method to identify matrix files from GEO FTP links
- [ ] Add method to selectively download only matrix files
- [ ] Implement matrix file parser to convert to clean TSV format
- [ ] Add support for both compressed (.gz) and uncompressed formats

#### 1.2 Create GEOMatrix Class
- [ ] Create new class to handle matrix-specific operations
- [ ] Implement methods to read matrix files and extract metadata
- [ ] Implement conversion to pandas DataFrame
- [ ] Add export functionality to TSV

### 2. CLI Integration

#### 2.1 Add New CLI Commands
- [ ] Create `geo-matrix` subcommand
- [ ] Add options for accession, output directory, and TSV conversion
- [ ] Integrate with existing download functionality

#### 2.2 Update Existing CLI
- [ ] Add matrix-specific options to existing download command
- [ ] Ensure backward compatibility

### 3. Testing

#### 3.1 Unit Tests
- [ ] Test matrix file identification
- [ ] Test matrix file parsing
- [ ] Test TSV conversion

#### 3.2 Integration Tests
- [ ] Test end-to-end workflow with real GEO accessions
- [ ] Test CLI commands

### 4. Documentation

#### 4.1 Update README
- [ ] Add section on GEO Matrix file support
- [ ] Include examples

#### 4.2 Update Documentation
- [ ] Add detailed documentation for new functionality
- [ ] Include examples in Python API usage
- [ ] Update command-line documentation

### 5. Final Steps

#### 5.1 Code Review
- [ ] Ensure code quality and style consistency
- [ ] Check for edge cases

#### 5.2 Version Update
- [ ] Update version number
- [ ] Update changelog

## Detailed Implementation Strategy

### Matrix File Identification
- Analyze GEO FTP structure to identify matrix files
- Matrix files are typically in a "matrix" subdirectory
- Example: https://ftp.ncbi.nlm.nih.gov/geo/series/GSE234nnn/GSE234190/matrix/
- Implement pattern matching to identify matrix files from FTP listings
- Handle different GEO series formats (GSEnnn, GSEnnnn, etc.)

### GEOMatrix Class Design
- Create a new class that inherits from appropriate base class
- Implement methods:
  - `__init__`: Initialize with GEO accession
  - `get_matrix_files`: Identify matrix files for a given accession
  - `download_matrix`: Download matrix files only
  - `parse_matrix`: Parse matrix file handling metadata rows (prefixed with !)
  - `to_dataframe`: Convert parsed matrix to pandas DataFrame
  - `to_tsv`: Export DataFrame to TSV format

### Matrix File Parsing Logic
- Read file line by line
- Identify and extract metadata lines (starting with !)
- Parse header row to get column names
- Parse data rows into a structured format
- Handle both tab-delimited and comma-delimited formats
- Support for compressed (.gz) files using gzip module

### CLI Integration
- Add new subcommand `geo-matrix` with options:
  - `--accession`: GEO accession number
  - `--output-dir`: Directory to save files
  - `--to-tsv`: Convert to TSV format
  - `--metadata-only`: Extract only metadata
- Update existing `download` command with option:
  - `--matrix-only`: Download only matrix files

### Testing Strategy
- Unit tests:
  - Mock FTP responses for testing matrix file identification
  - Use sample matrix files for testing parsing logic
  - Test conversion to DataFrame and TSV
- Integration tests:
  - Test with real GEO accessions
  - Verify downloaded files and parsed output
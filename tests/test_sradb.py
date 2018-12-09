"""Tests for sradb.py
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pytest
from pysradb import SRAdb


@pytest.fixture(scope="module")
def sradb_connection(conf_download_sradb_file):
    db_file = conf_download_sradb_file
    db = SRAdb(db_file)
    return db


def test_list_tables(sradb_connection):
    sra_tables = sradb_connection.list_tables()
    assert sra_tables == [
        'metaInfo', 'submission', 'study', 'sample', 'experiment', 'run',
        'sra', 'sra_ft', 'sra_ft_content', 'sra_ft_segments', 'sra_ft_segdir',
        'col_desc', 'fastq'
    ]


def test_list_fields(sradb_connection):
    fields = sradb_connection.list_fields('study')
    assert fields == [
        'study_ID', 'study_alias', 'study_accession', 'study_title',
        'study_type', 'study_abstract', 'broker_name', 'center_name',
        'center_project_name', 'study_description', 'related_studies',
        'primary_study', 'sra_link', 'study_url_link', 'xref_link',
        'study_entrez_link', 'ddbj_link', 'ena_link', 'study_attribute',
        'submission_accession', 'sradb_updated'
    ]


def test_desc_table(sradb_connection):
    names = sorted(sradb_connection.desc_table('sra_ft').name.tolist())
    assert names[:7] == [
        'SRR_bamFile', 'SRX_bamFile', 'SRX_fastqFTP', 'adapter_spec',
        'anonymized_name', 'base_caller', 'bases'
    ]


def test_all_row_counts(sradb_connection):
    assert sradb_connection.all_row_counts().loc['metaInfo', 'count'] == 2


def test_sra_metadata(sradb_connection):
    df = sradb_connection.sra_metadata('SRP017942')
    assert df['experiment_accession'][0] == 'SRX217028'


def test_sra_metadata2(sradb_connection):
    df = sradb_connection.sra_metadata(
        'SRP017942', expand_sample_attributes=True)
    assert df['transfected_with'][0] == '3xflag-gfp'


def test_search(sradb_connection):
    df = sradb_connection.search_sra(search_str="breast cancer")
    assert len(df.index)

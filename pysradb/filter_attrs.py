import warnings
import re
import numpy as np
import pandas as pd


def _get_sample_attr_keys(sample_attribute):
    if sample_attribute is None:
        return None, None
    sample_attribute_splitted = sample_attribute.split('||')
    sample_attribute_dict = dict(
        [str(attr).split(': ') for attr in sample_attribute_splitted])
    sample_attribute_keys = list(
        map(lambda x: x.lstrip(' ').replace(' ', '_').lower(),
            list(sample_attribute_dict.keys())))
    sample_attribute_values = list(
        map(lambda x: x.lower().rstrip(' ').replace(',', '__'),
            list(sample_attribute_dict.values())))
    return sample_attribute_keys, sample_attribute_values


def expand_sample_attribute_columns(metadata_df):
    """Expand sample attribute columns to individual columns.

    Since the sample_attribute column content can be different
    for differnt rows even if coming from the same project (SRP),
    we explicitly iterate through the rows to first determine
    what additional columns need to be created.


    Parameters
    ----------
    metadata_df: DataFrame
                 Dataframe as obtained from sra_metadata
                 or equivalent

    Returns
    -------
    expanded_df: DataFrame
                 Dataframe with additionals columns pertaining
                 to sample_attribute appended
    """
    additional_columns = []
    for idx, row in metadata_df.iterrows():
        sample_attribute = row['sample_attribute']
        sample_attribute_keys, _ = _get_sample_attr_keys(sample_attribute)
        if sample_attribute_keys:
            additional_columns += sample_attribute_keys
    additional_columns = list(sorted(set(additional_columns)))
    # if any of the additional column already exists
    # call the additional column  as *_expanded
    additional_columns = list(
        map(
            lambda x: x if x not in metadata_df.columns.tolist() else x + '_expanded',
            additional_columns))
    additional_columns = list(sorted(additional_columns))
    empty_df = pd.DataFrame(columns=additional_columns)
    metadata_df_expanded = pd.concat([metadata_df, empty_df], axis=1)
    for idx, row in metadata_df_expanded.iterrows():
        sample_attribute = row['sample_attribute']
        sample_attribute_keys, sample_attribute_values = _get_sample_attr_keys(
            sample_attribute)
        sample_attribute_keys = list(
            map(
                lambda x: x if x not in metadata_df.columns.tolist() else x + '_expanded',
                sample_attribute_keys))
        metadata_df_expanded.loc[
            idx, sample_attribute_keys] = sample_attribute_values
    return metadata_df_expanded


def guess_cell_type(sample_attribute):
    """Guess possible cell line from sample_attribute data.

    Parameters
    ----------
    sample_attribute: string
                      sample_attribute string as in the metadata column

    Returns
    -------
    cell_type: string
               Possible cell type of sample.
               Returns None if no match found.
    """
    sample_attribute = str(sample_attribute)
    cell_type = None
    if 'cell line:' in sample_attribute:
        x = re.search(r'cell line: \w+', sample_attribute)
        cell_type = x.group(0).strip('cell line: ').rstrip(' ').upper()
    if 'cell_line:' in sample_attribute:
        x = re.search(r'cell_line: \w+', sample_attribute)
        cell_type = x.group(0).strip('cell_line: ').rstrip(' ').upper()
    if 'cell-line:' in sample_attribute:
        x = re.search(r'cell-line: \w+', sample_attribute)
        cell_type = x.group(0).strip('cell-line: ').rstrip(' ').upper()
    if 'cell_type:' in sample_attribute:
        x = re.search(r'cell_type: \w+', sample_attribute)
        return x.group(0).strip('cell_type: ').rstrip(' ').upper()
    if 'source_name:' in sample_attribute:
        x = re.search(r'source_name: \w+', sample_attribute)
        cell_type = x.group(0).strip('source_name: ').rstrip(' ').upper()
    else:
        warnings.warn(
            'Couldn\'t parse {} for cell line'.format(sample_attribute),
            UserWarning)
    return cell_type


def guess_tissue_type(sample_attribute):
    """Guess tissue type from sample_attribute data.

    Parameters
    ----------
    sample_attribute: string
                      sample_attribute string as in the metadata column

    Returns
    -------
    tissue_type: string
               Possible cell type of sample.
               Returns None if no match found.
    """
    sample_attribute = str(sample_attribute)
    tissue_type = None
    if 'tissue: ' in sample_attribute:
        x = re.search(r'tissue: \w+', sample_attribute)
        tissue_type = x.group(0).strip('tissue: ').rstrip(' ').lower()
    else:
        warnings.warn('Couldn\'t parse {} for tissue'.format(sample_attribute),
                      UserWarning)
    return tissue_type


def guess_strain_type(sample_attribute):
    """Guess strain type from sample_attribute data.

    Parameters
    ----------
    sample_attribute: string
                      sample_attribute string as in the metadata column

    Returns
    -------
    strain_type: string
                 Possible cell type of sample.
                 Returns None if no match found.
    """
    sample_attribute = str(sample_attribute)
    strain_type = None
    if 'strain: ' in sample_attribute:
        x = re.search(r'strain: \w+', sample_attribute)
        strain_type = x.group(0).strip('strain: ').rstrip(' ').lower()
    else:
        warnings.warn('Couldn\'t parse {} for strain'.format(sample_attribute),
                      UserWarning)
    return strain_type

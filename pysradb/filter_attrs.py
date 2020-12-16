import re
import warnings

import numpy as np
import pandas as pd


def _get_sample_attr_keys(sample_attribute):
    if sample_attribute is None:
        return None, None
    sample_attribute_splitted = sample_attribute.split("||")
    split_by_colon = [
        str(attr).strip().split(": ") for attr in sample_attribute_splitted
    ]

    # Iterate once more to consider first one as the key
    # and remaining as the value
    # This is because of bad annotations like in this example
    # Example: isolate: not applicable || organism: Mus musculus || cell_line: 17-Cl1 ||\
    # infect: MHV-A59 || time point: 5: hour || compound: cycloheximide ||\
    # sequencing protocol: RiboSeq || biological repeat: long read sequencing
    # Notice the `time: 5: hour`
    # sample_attribute: investigation type: metagenome || project name: Landsort Depth 20090415 transect ||
    # sequencing method: 454 || collection date: 2009-04-15 || ammonium: 8.7: Ã‚ÂµM || chlorophyll: 0: Ã‚Âµg/L ||
    # dissolved oxygen: -1.33: Ã‚Âµmol/kg || nitrate: 0.02: Ã‚ÂµM || nitrogen: 0: Ã‚ÂµM ||
    # environmental package: water || geographic location (latitude): 58.6: DD ||
    # geographic location (longitude): 18.2: DD || geographic location (country and/or sea,region): Baltic Sea ||
    # environment (biome): 00002150 || environment (feature): 00002150 || environment (material): 00002150 ||
    # depth: 400: m || Phosphate:  || Total phosphorous:  || Silicon:
    # Handle empty cases as above
    split_by_colon = [attr for attr in split_by_colon if len(attr) >= 2]

    for index, element in enumerate(split_by_colon):
        if len(element) > 2:
            key = element[0].strip()
            value = ":".join(element[1:]).strip()
            split_by_colon[index] = [key, value]

    try:
        sample_attribute_dict = dict(split_by_colon)
    except ValueError:
        print("This is most likely a bug, please report it upstream.")
        print(("sample_attribute: {}".format(sample_attribute)))
        raise
    sample_attribute_keys = list(
        map(
            lambda x: re.sub(r"\s+", " ", x.strip().replace(" ", "_").lower()),
            list(sample_attribute_dict.keys()),
        )
    )
    sample_attribute_values = list(
        map(
            lambda x: re.sub(r"\s+", " ", x.strip().lower().strip().replace(",", "__")),
            list(sample_attribute_dict.values()),
        )
    )
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
    metadata_df = metadata_df.copy()
    for idx, row in metadata_df.iterrows():
        sample_attribute = row["sample_attribute"]
        if not sample_attribute:
            continue
        sample_attribute = sample_attribute.strip()
        sample_attribute_keys, _ = _get_sample_attr_keys(sample_attribute)
        if sample_attribute_keys:
            additional_columns += sample_attribute_keys
    additional_columns = list(sorted(set(additional_columns)))
    # if any of the additional column already exists
    # call the additional column  as *_expanded
    additional_columns = list(
        map(
            lambda x: x if x not in metadata_df.columns.tolist() else x + "_expanded",
            additional_columns,
        )
    )
    additional_columns = list(sorted(additional_columns))
    empty_df = pd.DataFrame(columns=additional_columns)
    metadata_df_expanded = pd.concat([metadata_df, empty_df], axis=1)
    for idx, row in metadata_df_expanded.iterrows():
        sample_attribute = row["sample_attribute"]
        sample_attribute_keys, sample_attribute_values = _get_sample_attr_keys(
            sample_attribute
        )
        if sample_attribute_keys:
            sample_attribute_keys = list(
                map(
                    lambda x: x
                    if x not in metadata_df.columns.tolist()
                    else x + "_expanded",
                    sample_attribute_keys,
                )
            )
        metadata_df_expanded.loc[idx, sample_attribute_keys] = sample_attribute_values
    if np.nan in metadata_df_expanded.columns.tolist():
        del metadata_df_expanded[np.nan]
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
    if "cell line:" in sample_attribute:
        x = re.search(r"cell line: \w+", sample_attribute)
        cell_type = re.sub(r"\s+", " ", x.group(0).lstrip("cell line:").lower().strip())
    if "cell_line:" in sample_attribute:
        x = re.search(r"cell_line: \w+", sample_attribute)
        cell_type = re.sub(r"\s+", " ", x.group(0).lstrip("cell_line:").lower().strip())
    if "cell-line:" in sample_attribute:
        x = re.search(r"cell-line: \w+", sample_attribute)
        cell_type = re.sub(r"\s+", " ", x.group(0).lstrip("cell-line:").lower().strip())
    if "cell_type:" in sample_attribute:
        x = re.search(r"cell_type: \w+", sample_attribute)
        return re.sub(r"\s+", " ", x.group(0).lstrip("cell_type:").lower().strip())
    if "source_name:" in sample_attribute:
        x = re.search(r"source_name: \w+", sample_attribute)
        cell_type = re.sub(
            r"\s+", " ", x.group(0).lstrip("source_name:").lower().strip()
        )
    else:
        warnings.warn(
            "Couldn't parse {} for cell line".format(sample_attribute), UserWarning
        )
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
    if "tissue: " in sample_attribute:
        x = re.search(r"tissue: \w+", sample_attribute)
        tissue_type = re.sub(r"\s+", " ", x.group(0).lstrip("tissue:").lower().strip())
    else:
        warnings.warn(
            "Couldn't parse {} for tissue".format(sample_attribute), UserWarning
        )
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
    if "strain: " in sample_attribute:
        x = re.search(r"strain: \w+", sample_attribute)
        strain_type = re.sub(r"\s+", " ", x.group(0).lstrip("strain:").lower().strip())
    else:
        warnings.warn(
            "Couldn't parse {} for strain".format(sample_attribute), UserWarning
        )
    return strain_type

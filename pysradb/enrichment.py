import concurrent.futures
import importlib.util
import json
import math
import os
import time

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from rich.console import Console
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from typing_extensions import TypedDict

from .utils import confirm

console = Console()
_EMBEDDING_MODELS = {}


def _get_embedding_model(model_name: str):
    if model_name not in _EMBEDDING_MODELS:
        console.print("Setting up embedding model...")
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        _EMBEDDING_MODELS[model_name] = SentenceTransformer(model_name)
        console.print("Embedding model set up complete")
    return _EMBEDDING_MODELS[model_name]


def _warn_if_vllm_missing():
    if importlib.util.find_spec("vllm") is None:
        console.print(
            "[yellow]vLLM backend selected, but the optional 'vllm' dependency "
            "is not installed. Install it with `pip install pysradb[vllm]` "
            "(Linux) if you plan to run a local vLLM server. If you are using "
            "a remote vLLM endpoint, you can ignore this warning.[/yellow]"
        )


def enrich_df(
    detailed_df,
    basic_cols: list[str] = [],
    enrichment_backend="ollama/granite4:3b",
    embedding_model="abhinand/MedEmbed-large-v0.1",
):
    def _coerce_str(value):
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, str):
            return value
        return str(value)

    def _normalized(value):
        text = _coerce_str(value)
        if text is None:
            return None
        return text.strip().lower()

    def filter_dict(d: dict, keys: list[str]) -> str:
        return json.dumps({k: d[k] for k in keys if k in d})

    model = _get_embedding_model(embedding_model)
    console.print("Enriching metadata in progress...")

    if enrichment_backend.startswith("ollama/"):
        ollama_model = enrichment_backend.split("ollama/")[-1]
        llm = ChatOllama(
            model=ollama_model,
            temperature=0,
        )
    elif enrichment_backend.startswith("lmstudio/"):
        lmstudio_model = enrichment_backend.split("lmstudio/")[-1]
        llm = ChatOpenAI(
            model=lmstudio_model,
            base_url="http://localhost:1234/v1",
            api_key=None,
            temperature=0,
        )
    elif enrichment_backend.startswith("vllm/"):
        _warn_if_vllm_missing()
        vllm_model = enrichment_backend.split("vllm/")[-1]
        llm = ChatOpenAI(
            model=vllm_model,
            base_url="http://localhost:8000/v1",
            api_key="EMPTY",  # type: ignore
            temperature=0,
        )
    elif enrichment_backend == "vllm":
        _warn_if_vllm_missing()
        llm = ChatOpenAI(
            model="ibm-granite/granite-4.0-micro",
            base_url="http://localhost:8000/v1",
            api_key="EMPTY",  # type: ignore
            temperature=0,
        )
    else:
        raise ValueError(
            (
                f"Unsupported enrichment_backend: {enrichment_backend}. "
                "Supported formats: 'ollama/<model>', 'lmstudio/<model>', "
                "'vllm/<model>', or 'vllm'"
            )
        )

    def get_relevant_keys(term: str, embeddings, keys: list[str]) -> list[str]:
        if len(keys) == 0:
            return []
        query = model.encode(term, convert_to_tensor=True)
        similarities = util.cos_sim(query, embeddings)
        # Keep dimension to handle single-element case
        similarities = similarities.squeeze(0)
        if similarities.dim() == 0:
            # Single element case
            return [keys[0]] if similarities.item() > 0.8 else []
        relevant_keys = []
        for i, similarity in enumerate(similarities):
            if similarity > 0.8:
                relevant_keys.append(keys[i])
        return relevant_keys

    def get_sex_keys(embeddings, keys: list[str]):
        return get_relevant_keys("sex", embeddings, keys) + get_relevant_keys(
            "gender", embeddings, keys
        )

    def get_age_keys(embeddings, keys: list[str]):
        return get_relevant_keys("age", embeddings, keys)

    def get_cell_type_keys(embeddings, keys: list[str]):
        return get_relevant_keys("cell type", embeddings, keys) + get_relevant_keys(
            "histological", embeddings, keys
        )

    def get_tissue_keys(embeddings, keys: list[str]):
        return (
            get_relevant_keys("tissue", embeddings, keys)
            + get_relevant_keys("organ", embeddings, keys)
            + get_relevant_keys("body site", embeddings, keys)
            + get_relevant_keys("tumor site", embeddings, keys)
        )

    def get_phenotype_keys(embeddings, keys: list[str]):
        return get_relevant_keys("phenotype", embeddings, keys)

    def get_strain_keys(embeddings, keys: list[str]):
        return get_relevant_keys("strain", embeddings, keys)

    def get_ethnicity_keys(embeddings, keys: list[str]):
        return get_relevant_keys("ethnicity", embeddings, keys) + get_relevant_keys(
            "population", embeddings, keys
        )

    def get_disease_keys(embeddings, keys: list[str]):
        return (
            get_relevant_keys("disease", embeddings, keys)
            + get_relevant_keys("tumor", embeddings, keys)
            + get_relevant_keys("infection", embeddings, keys)
            + get_relevant_keys("cancer", embeddings, keys)
            + get_relevant_keys("study disease", embeddings, keys)
            + get_tissue_keys(embeddings, keys)
            + get_relevant_keys("source", embeddings, keys)
            + get_relevant_keys("subject status", embeddings, keys)
        )

    # def get_host_keys(embeddings, keys: list[str]):
    #     return get_relevant_keys("host", embeddings, keys)

    def get_refined_keys(raw_keys: list[str]) -> list[str]:
        keys = []
        for key in raw_keys:
            refined_key = key.rstrip("0123456789")
            keys.append(
                refined_key.replace("ArrayExpress-", "")
                .lower()
                .replace("-", " ")
                .replace("%", "")
                .replace("*", "")
                # .replace("_", " ") <-- muted by choice
            )
        return keys

    system_prompt = "{sys_prompt}"
    user_prompt = "information: {info}"

    na_strings = ["missing", "not applicable", "unknown", "na", "n/a", "not collected"]

    prompt_template = ChatPromptTemplate(
        [("system", system_prompt), ("user", user_prompt)]
    )

    class TissueOutput(TypedDict):
        """Inferred tissue name."""

        tissue: str | None

    class DiseaseOutput(TypedDict):
        """Inferred disease name."""

        disease: str | None

    class State(TypedDict):
        attributes: dict
        embeddings: object
        raw_keys: list[str]
        age: str | None
        sex: str | None
        ethnicity: str | None
        phenotype: str | None
        cell_type: str | None
        tissue: str | None
        strain: str | None
        disease: str | None

    # Nodes
    def estimate_age(state: State):
        """Function to estimate age from available data"""
        keys = get_age_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            age_value = state["attributes"][key]
            age_text = _coerce_str(age_value)
            if not age_text:
                return {"age": None}
            if _normalized(age_text) in na_strings:
                return {"age": None}
            else:
                return {"age": age_text}
        else:
            return {"age": None}

    def estimate_sex(state: State):
        """Function to estimate sex"""
        # This counts on the phenomenon that there is always one attribute related
        # to sex (if it is there) and it is quite unambiguous
        keys = get_sex_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            sex_value = _normalized(state["attributes"].get(key))
            if sex_value in ["male", "m"]:
                return {"sex": "Male"}
            elif sex_value in ["female", "f"]:
                return {"sex": "Female"}
            else:
                return {"sex": None}
        else:
            return {"sex": None}

    def estimate_tissue(state: State):
        keys = get_tissue_keys(state["embeddings"], state["raw_keys"])
        if keys:
            if len(keys) == 1:
                tissue = state["attributes"][keys.pop()]
                tissue_text = _coerce_str(tissue)
                if tissue_text:
                    if _normalized(tissue_text) in na_strings:
                        return {"tissue": None}
                    else:
                        return {"tissue": tissue_text}
                else:
                    return {"tissue": None}
            else:
                info_json = filter_dict(state["attributes"], keys)
                sys_prompt = """
                    You will infer the correct tissue from the given information.
                    Do not use information information that are not clear tissue names.
                    For example, do not use numbers, URLs and pathology for tissue
                    names. You can use an organ name as tissue too.
                """
                prompt = prompt_template.invoke(
                    {"sys_prompt": sys_prompt, "info": info_json}
                )
                structured_llm = llm.with_structured_output(TissueOutput)
                result = structured_llm.invoke(prompt)
                return {"tissue": result["tissue"]}  # type: ignore
        else:
            return {"tissue": None}

    def estimate_strain(state: State):
        keys = get_strain_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            if "host" not in key:
                return {"strain": state["attributes"][key]}
            else:
                return {"strain": None}
        else:
            return {"strain": None}

    def estimate_phenotype(state: State):
        keys = get_phenotype_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            if "host" not in key:
                return {"phenotype": state["attributes"][key]}
            else:
                return {"phenotype": None}
        else:
            return {"phenotype": None}

    def estimate_cell_type(state: State):
        keys = get_cell_type_keys(state["embeddings"], state["raw_keys"])
        if keys:
            return {"cell_type": state["attributes"][keys.pop()]}
        else:
            return {"cell_type": None}

    def estimate_ethnicity(state: State):
        keys = get_ethnicity_keys(state["embeddings"], state["raw_keys"])
        if keys:
            return {"ethnicity": state["attributes"][keys.pop()]}
        else:
            return {"ethnicity": None}

    def estimate_disease(state: State):
        """Function to estimate disease from available data."""
        keys = get_disease_keys(state["embeddings"], state["raw_keys"])
        if keys:
            # If there's an explicit "disease" key, use it directly
            if "disease" in keys:
                disease_value = _coerce_str(state["attributes"].get("disease"))
                if disease_value is None:
                    return {"disease": None}
                if _normalized(disease_value) in na_strings:
                    return {"disease": None}
                return {"disease": disease_value}
            # Otherwise, use LLM to infer from available data
            info_json = filter_dict(state["attributes"], keys)
            sys_prompt = """
                You will infer the disease or condition from the given information.
                Consider all available data including disease names, tumor types,
                infection status, cancer types, and subject health status.
                If the subject is healthy or normal, return null.
                Do not use unclear values like numbers, URLs, or file paths.
                Return only the disease/condition name or null if none can be inferred.
            """
            prompt = prompt_template.invoke(
                {"sys_prompt": sys_prompt, "info": info_json}
            )
            structured_llm = llm.with_structured_output(DiseaseOutput)
            result = structured_llm.invoke(prompt)
            return {"disease": result["disease"] if result else None}  # type: ignore
        else:
            return {"disease": None}

    workflow_graph_builder = StateGraph(State)

    workflow_graph_builder.add_node("estimate_age", estimate_age)
    workflow_graph_builder.add_node("estimate_sex", estimate_sex)
    workflow_graph_builder.add_node("estimate_tissue", estimate_tissue)
    workflow_graph_builder.add_node("estimate_strain", estimate_strain)
    workflow_graph_builder.add_node("estimate_phenotype", estimate_phenotype)
    workflow_graph_builder.add_node("estimate_cell_type", estimate_cell_type)
    workflow_graph_builder.add_node("estimate_ethnicity", estimate_ethnicity)
    workflow_graph_builder.add_node("estimate_disease", estimate_disease)

    workflow_graph_builder.add_edge(START, "estimate_age")
    workflow_graph_builder.add_edge(START, "estimate_sex")
    workflow_graph_builder.add_edge(START, "estimate_tissue")
    workflow_graph_builder.add_edge(START, "estimate_strain")
    workflow_graph_builder.add_edge(START, "estimate_phenotype")
    workflow_graph_builder.add_edge(START, "estimate_cell_type")
    workflow_graph_builder.add_edge(START, "estimate_ethnicity")
    workflow_graph_builder.add_edge(START, "estimate_disease")

    workflow_graph_builder.add_edge("estimate_age", END)
    workflow_graph_builder.add_edge("estimate_sex", END)
    workflow_graph_builder.add_edge("estimate_tissue", END)
    workflow_graph_builder.add_edge("estimate_strain", END)
    workflow_graph_builder.add_edge("estimate_phenotype", END)
    workflow_graph_builder.add_edge("estimate_cell_type", END)
    workflow_graph_builder.add_edge("estimate_ethnicity", END)
    workflow_graph_builder.add_edge("estimate_disease", END)

    workflow = workflow_graph_builder.compile()

    ENRICHED_COLS = [
        "age",
        "sex",
        "ethnicity",
        "phenotype",
        "cell_type",
        "tissue",
        "strain",
        "disease",
    ]

    # Pandas can infer numeric dtypes for pre-existing enrichment columns.
    # Force object-compatible columns so string outputs (e.g., "PDX1") do not
    # fail assignment on newer pandas versions.
    for col in ENRICHED_COLS:
        if col in detailed_df.columns:
            detailed_df[col] = detailed_df[col].astype("object")
        else:
            detailed_df[col] = pd.Series(pd.NA, index=detailed_df.index, dtype="object")

    max_preview_rows = 15
    if len(detailed_df) > max_preview_rows:
        proceed_all = confirm(
            (
                f"Dataframe has {len(detailed_df)} rows. "
                "More rows will take longer to enrich. "
                "Enrich all rows? Choose 'n' to enrich only the first 15 for "
                "a quick review."
            )
        )
        if not proceed_all:
            detailed_df = detailed_df.head(max_preview_rows).copy()

    attribute_cols = (
        [col for col in detailed_df.columns if col not in basic_cols]
        if basic_cols
        else list(detailed_df.columns)
    )
    refined_keys = get_refined_keys(attribute_cols)
    key_embeddings = model.encode(refined_keys, convert_to_tensor=True)

    def _enrich_row(item):
        i, each_row = item
        state = workflow.invoke(
            {
                "attributes": each_row.to_dict(),
                "embeddings": key_embeddings,
                "raw_keys": attribute_cols,
            }  # type: ignore
        )
        return i, {col: state.get(col) for col in ENRICHED_COLS}

    rows = list(detailed_df[attribute_cols].iterrows())
    start_time = time.perf_counter()
    if rows:
        max_workers = min(8, os.cpu_count() or 4, len(rows))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i, enriched in tqdm(
                executor.map(_enrich_row, rows),
                total=len(rows),
                desc="Enriching rows",
            ):
                for col, value in enriched.items():
                    detailed_df.loc[i, col] = value  # type: ignore
    elapsed = time.perf_counter() - start_time
    console.print(f"Enrichment completed in {elapsed:.2f} seconds.")
    # existing_basic_cols = (
    #     [col for col in basic_cols if col in detailed_df.columns]
    #     if basic_cols
    #     else attribute_cols
    # )
    id_col = None
    if "Sample" in detailed_df.columns:
        id_col = "Sample"
    elif "Accession" in detailed_df.columns:
        id_col = "Accession"
    elif "experiment_accession" in detailed_df.columns:
        id_col = "experiment_accession"

    if id_col is None:
        raise KeyError(
            "Expected one of ['Sample', 'Accession', 'experiment_accession'] "
            "in detailed_df."
        )

    return detailed_df[[id_col] + ENRICHED_COLS]

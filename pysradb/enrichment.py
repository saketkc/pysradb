import json
import os

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from rich.console import Console
from sentence_transformers import SentenceTransformer, util
from torch import Tensor
from typing_extensions import TypedDict

console = Console()


def enrich_df(
    detailed_df: pd.DataFrame,
    basic_cols: list[str] = [],
    enrichment_backend="ollama/granite4:3b",
):
    def filter_dict(d: dict, keys: list[str]) -> str:
        return json.dumps({k: d[k] for k in keys if k in d})

    console.print("Setting up embedding model...")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    model = SentenceTransformer("abhinand/MedEmbed-large-v0.1")
    console.print("Embedding model set up complete")
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
        vllm_model = enrichment_backend.split("vllm/")[-1]
        llm = ChatOpenAI(
            model=vllm_model,
            base_url="http://localhost:8000/v1",
            api_key="EMPTY",  # type: ignore
            temperature=0,
        )
    elif enrichment_backend == "vllm":
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

    def get_relevant_keys(term: str, embeddings: Tensor, keys: list[str]) -> list[str]:
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

    def get_sex_keys(embeddings: Tensor, keys: list[str]):
        return get_relevant_keys("sex", embeddings, keys) + get_relevant_keys(
            "gender", embeddings, keys
        )

    def get_age_keys(embeddings: Tensor, keys: list[str]):
        return get_relevant_keys("age", embeddings, keys)

    def get_cell_type_keys(embeddings: Tensor, keys: list[str]):
        return get_relevant_keys("cell type", embeddings, keys) + get_relevant_keys(
            "histological", embeddings, keys
        )

    def get_tissue_keys(embeddings: Tensor, keys: list[str]):
        return (
            get_relevant_keys("tissue", embeddings, keys)
            + get_relevant_keys("organ", embeddings, keys)
            + get_relevant_keys("body site", embeddings, keys)
            + get_relevant_keys("tumor site", embeddings, keys)
        )

    def get_phenotype_keys(embeddings: Tensor, keys: list[str]):
        return get_relevant_keys("phenotype", embeddings, keys)

    def get_strain_keys(embeddings: Tensor, keys: list[str]):
        return get_relevant_keys("strain", embeddings, keys)

    def get_ethnicity_keys(embeddings: Tensor, keys: list[str]):
        return get_relevant_keys("ethnicity", embeddings, keys) + get_relevant_keys(
            "population", embeddings, keys
        )

    def get_disease_keys(embeddings: Tensor, keys: list[str]):
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

    # def get_host_keys(embeddings: Tensor, keys: list[str]):
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
        embeddings: Tensor
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
            if not age_value:
                return {"age": None}
            if age_value.strip().lower() in na_strings:
                return {"age": None}
            else:
                return {"age": age_value}
        else:
            return {"age": None}

    def estimate_sex(state: State):
        """Function to estimate sex"""
        # This counts on the phenomenon that there is always one attribute related
        # to sex (if it is there) and it is quite unambiguous
        keys = get_sex_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            if state["attributes"][key].lower() in ["male", "m"]:
                return {"sex": "Male"}
            elif state["attributes"][key].lower() in ["female", "f"]:
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
                if tissue:
                    if tissue.lower() in na_strings:
                        return {"tissue": None}
                    else:
                        return {"tissue": tissue}
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
                disease_value = state["attributes"].get("disease")
                if disease_value is None:
                    return {"disease": None}
                if not isinstance(disease_value, str):
                    disease_value = str(disease_value)
                if disease_value.strip().lower() in na_strings:
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

    attribute_cols = (
        [col for col in detailed_df.columns if col not in basic_cols]
        if basic_cols
        else list(detailed_df.columns)
    )
    refined_keys = get_refined_keys(attribute_cols)
    key_embeddings = model.encode(refined_keys, convert_to_tensor=True)
    for i, each_row in detailed_df[attribute_cols].iterrows():
        state = workflow.invoke(
            {
                "attributes": each_row.to_dict(),
                "embeddings": key_embeddings,
                "raw_keys": attribute_cols,
            }  # type: ignore
        )
        for col in ENRICHED_COLS:
            detailed_df.loc[i, col] = state.get(col)  # type: ignore
    # existing_basic_cols = (
    #     [col for col in basic_cols if col in detailed_df.columns]
    #     if basic_cols
    #     else attribute_cols
    # )
    return detailed_df[["experiment_accession"] + ENRICHED_COLS]

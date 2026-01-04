import json
from typing import Literal

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from rich.console import Console
from sentence_transformers import SentenceTransformer, util
from torch import Tensor
from typing_extensions import TypedDict

# Rich console for formatted output
_console = Console(stderr=True)


class EnrichmentError(Exception):
    """Base exception for enrichment-related errors."""

    pass


class ModelLoadingError(EnrichmentError):
    """Exception raised when model loading fails."""

    def __init__(self, model_name: str, original_error: Exception):
        self.model_name = model_name
        self.original_error = original_error
        self.message = (
            f"Failed to load model '{model_name}': {original_error}\n"
            "Please ensure the model is available and dependencies are installed."
        )
        super().__init__(self.message)


class LLMInferenceError(EnrichmentError):
    """Exception raised when LLM inference fails."""

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        self.message = (
            f"LLM inference failed during '{operation}': {original_error}\n"
            "Please ensure the LLM backend is running and the requested model is available."
        )
        super().__init__(self.message)


class OllamaConnectionError(EnrichmentError):
    """Exception raised when the configured LLM backend is not reachable.

    This class provides backend-aware guidance. If the active backend
    appears to be an Ollama backend, it includes Ollama-specific steps.
    """

    def __init__(self, backend: str | None = None):
        # Determine active backend if not provided
        active_backend = backend or globals().get("_llm_backend")

        if active_backend and active_backend.startswith("ollama"):
            # Extract model part for user guidance
            parts = active_backend.split("/", 1)
            model_hint = parts[1] if len(parts) > 1 else "<model>"
            self.message = (
                f"Cannot connect to Ollama server or load model '{model_hint}'.\n"
                "Please ensure Ollama is installed and running:\n"
                "  1. Install Ollama from https://ollama.ai\n"
                "  2. Start Ollama with 'ollama serve'\n"
                f"  3. Pull the required model with 'ollama pull {model_hint}'"
            )
        else:
            # Generic guidance for other backends
            provider = (
                active_backend.split("/", 1)[0] if active_backend else "LLM backend"
            )
            self.message = (
                f"Cannot connect to {provider} or load the configured model.\n"
                "Please ensure the backend/service is installed, running, and the requested model is available."
            )

        super().__init__(self.message)


class _EnrichmentErrorTracker:
    """Tracks errors during enrichment to provide a clean summary."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all error counters."""
        self.llm_connection_errors = 0
        self.llm_inference_errors = 0
        self.row_processing_errors = 0
        self.total_rows = 0
        self._connection_error_warned = False

    def record_llm_connection_error(self):
        """Record an LLM connection error."""
        self.llm_connection_errors += 1

    def record_llm_inference_error(self):
        """Record an LLM inference error."""
        self.llm_inference_errors += 1

    def record_row_error(self):
        """Record a row processing error."""
        self.row_processing_errors += 1

    def is_connection_error(self, error: Exception) -> bool:
        """Check if the error is a connection-related error."""
        error_str = str(error).lower()
        return (
            "connection refused" in error_str
            or "errno 61" in error_str
            or "connection error" in error_str
            or "connect call failed" in error_str
        )

    def warn_connection_error_once(self):
        """Warn about connection error only once."""
        if not self._connection_error_warned:
            self._connection_error_warned = True
            # Determine provider for a more helpful message
            active_backend = globals().get("_llm_backend")
            provider = (
                active_backend.split("/", 1)[0] if active_backend else "LLM backend"
            )
            if provider == "ollama":
                _console.print(
                    "[yellow]Warning[/yellow]  Ollama server not reachable - "
                    "LLM-based inference will be skipped."
                )
            elif provider == "lmstudio":
                _console.print(
                    "[yellow]Warning[/yellow]  LM Studio not reachable at http://localhost:1234 - "
                    "LLM-based inference will be skipped."
                )
            else:
                _console.print(
                    f"[yellow]Warning[/yellow]  {provider} backend not reachable - "
                    "LLM-based inference will be skipped."
                )

    def get_summary(self) -> str | None:
        """Get a summary of errors encountered, or None if no errors."""
        issues = []
        if self.llm_connection_errors > 0:
            issues.append(
                f"[dim]LLM unavailable ({self.llm_connection_errors} fields skipped)[/dim]"
            )
        if self.llm_inference_errors > 0:
            issues.append(
                f"[dim]LLM inference errors ({self.llm_inference_errors})[/dim]"
            )
        if self.row_processing_errors > 0:
            issues.append(
                f"[dim]Row errors ({self.row_processing_errors}/{self.total_rows})[/dim]"
            )

        if issues:
            return ", ".join(issues)
        return None

    def print_summary(self):
        """Print a formatted summary of any issues encountered."""
        summary = self.get_summary()
        if summary:
            _console.print(
                f"[yellow]Warning[/yellow]  Enrichment completed with issues: {summary}"
            )


# Global error tracker instance
_error_tracker = _EnrichmentErrorTracker()


def filter_dict(d: dict, keys: list[str]) -> str:
    return json.dumps({k: d[k] for k in keys if k in d})


def filter_dict_to_dict(d: dict, keys: list[str]) -> dict:
    return {k: d[k] for k in keys if k in d}


# Lazy initialization of models to avoid import-time failures
# Lazy initialization of models to avoid import-time failures
_embedding_model = None
_llm = None
# Currently active backend string (e.g., "ollama/phi3" or "lmstudio/my-model").
# This is set by `enrich_df` so nodes can call `_get_llm()` without passing
# the backend explicitly.
_llm_backend: str | None = None


def _get_embedding_model() -> SentenceTransformer:
    """Lazily load the sentence transformer model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            _embedding_model = SentenceTransformer("abhinand/MedEmbed-large-v0.1")
        except Exception as e:
            raise ModelLoadingError("abhinand/MedEmbed-large-v0.1", e)
    return _embedding_model


def _get_llm(backend: str | None = None):
    """Lazily initialize an LLM client for the requested backend.

    Supported backend prefixes:
      - "ollama/{model}"
      - "lmstudio/{model}"

    If `backend` is None, the function will use the module-level
    `_llm_backend` value which is set by `enrich_df`.
    """
    global _llm, _llm_backend

    if backend is None:
        backend = _llm_backend

    # Default to Ollama granite4 if nothing provided
    if not backend:
        backend = "ollama/granite4:3b"

    # If we already have an LLM instance for the same backend, reuse it
    if _llm is not None and _llm_backend == backend:
        return _llm

    # Parse provider and model
    if "/" in backend:
        provider, model_name = backend.split("/", 1)
    else:
        # Assume ollama model name if no prefix
        provider = "ollama"
        model_name = backend

    try:
        if provider == "ollama":
            # ChatOllama expects the model name (e.g., "granite4:3b" or "phi3")
            _llm = ChatOllama(model=model_name, temperature=0)
        elif provider == "lmstudio":
            # Use ChatOpenAI pointed at a local LM Studio OpenAI-compatible API
            try:
                from langchain_openai import ChatOpenAI  # type: ignore

                _llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=0.0,
                    base_url="http://localhost:1234/v1",
                    api_key="not-needed",
                )
            except Exception as e:
                raise ModelLoadingError(backend, e)
        else:
            # Unknown provider: try to fall back to Ollama with full backend
            _llm = ChatOllama(model=model_name, temperature=0)
    except ModelLoadingError:
        raise
    except Exception as e:
        raise ModelLoadingError(backend, e)

    _llm_backend = backend
    return _llm


def get_relevant_keys(term: str, embeddings: Tensor, keys: list[str]) -> list[str]:
    """Find keys that are semantically similar to the given term.

    Args:
        term: The term to search for.
        embeddings: Pre-computed embeddings for the keys.
        keys: List of attribute keys to search.

    Returns:
        List of keys with similarity > 0.8 to the term.

    Raises:
        ModelLoadingError: If the embedding model cannot be loaded.
    """
    if len(keys) == 0:
        return []

    try:
        model = _get_embedding_model()
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
    except ModelLoadingError:
        raise
    except Exception:
        # Silently handle similarity computation errors
        return []


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


def get_host_keys(embeddings: Tensor, keys: list[str]):
    return get_relevant_keys("host", embeddings, keys)


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

prompt_template = ChatPromptTemplate([("system", system_prompt), ("user", user_prompt)])


class AgeOutput(BaseModel):
    """Inferred age in unit of days"""

    age: float


class SexOutput(TypedDict):
    """Inferred sex. Allowed values are M and F."""

    sex: Literal["Male", "Female"] | None


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
    sex: Literal["Male", "Female"] | None
    ethnicity: str | None
    phenotype: str | None
    cell_type: str | None
    tissue: str | None
    strain: str | None
    disease: str | None


# Nodes
def estimate_age(state: State):
    """Function to estimate age from available data."""
    try:
        keys = get_age_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            age_value = state["attributes"].get(key)
            if age_value is None:
                return {"age": None}
            if not isinstance(age_value, str):
                age_value = str(age_value)
            if age_value.strip().lower() in na_strings:
                return {"age": None}
            else:
                return {"age": age_value}
        else:
            return {"age": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"age": None}


def estimate_sex(state: State):
    """Function to estimate sex (either M for Male or F for Female)."""
    try:
        # This counts on the phenomenon that there is always one attribute related
        # to sex (if it is there) and it is quite unambiguous
        keys = get_sex_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            sex_value = state["attributes"].get(key)
            if sex_value is None:
                return {"sex": None}
            if not isinstance(sex_value, str):
                sex_value = str(sex_value)
            if sex_value.lower() in ["male", "m"]:
                return {"sex": "M"}
            elif sex_value.lower() in ["female", "f"]:
                return {"sex": "F"}
            else:
                return {"sex": None}
        else:
            return {"sex": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"sex": None}


def estimate_tissue(state: State):
    """Function to estimate tissue from available data."""
    try:
        keys = get_tissue_keys(state["embeddings"], state["raw_keys"])
        if keys:
            if len(keys) == 1:
                tissue = state["attributes"].get(keys.pop())
                if tissue is None:
                    return {"tissue": None}
                if not isinstance(tissue, str):
                    tissue = str(tissue)
                if tissue.lower() in na_strings:
                    return {"tissue": None}
                else:
                    return {"tissue": tissue}
            else:
                info_json = filter_dict(state["attributes"], keys)
                sys_prompt = """
                    You will infer the correct tissue from the given information.
                    Do not use information information that are not clear tissue names.
                    For example, do not use numbers, URLs and pathology for tissue names.
                    You can use an organ name as tissue too.
                """
                try:
                    llm = _get_llm()
                    prompt = prompt_template.invoke(
                        {"sys_prompt": sys_prompt, "info": info_json}
                    )
                    structured_llm = llm.with_structured_output(TissueOutput)
                    result = structured_llm.invoke(prompt)
                    return {"tissue": result["tissue"] if result else None}  # type: ignore
                except Exception as llm_error:
                    if _error_tracker.is_connection_error(llm_error):
                        _error_tracker.record_llm_connection_error()
                        _error_tracker.warn_connection_error_once()
                    else:
                        _error_tracker.record_llm_inference_error()
                    # Fallback: return the first tissue key's value
                    first_tissue = state["attributes"].get(keys[0])
                    if first_tissue and str(first_tissue).lower() not in na_strings:
                        return {"tissue": str(first_tissue)}
                    return {"tissue": None}
        else:
            return {"tissue": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"tissue": None}


def estimate_strain(state: State):
    """Function to estimate strain from available data."""
    try:
        keys = get_strain_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            if "host" not in key:
                strain_value = state["attributes"].get(key)
                if strain_value is not None:
                    return {"strain": str(strain_value)}
            return {"strain": None}
        else:
            return {"strain": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"strain": None}


def estimate_phenotype(state: State):
    """Function to estimate phenotype from available data."""
    try:
        keys = get_phenotype_keys(state["embeddings"], state["raw_keys"])
        if keys:
            key = keys.pop()
            if "host" not in key:
                phenotype_value = state["attributes"].get(key)
                if phenotype_value is not None:
                    return {"phenotype": str(phenotype_value)}
            return {"phenotype": None}
        else:
            return {"phenotype": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"phenotype": None}


def estimate_cell_type(state: State):
    """Function to estimate cell type from available data."""
    try:
        keys = get_cell_type_keys(state["embeddings"], state["raw_keys"])
        if keys:
            cell_type_value = state["attributes"].get(keys.pop())
            if cell_type_value is not None:
                return {"cell_type": str(cell_type_value)}
        return {"cell_type": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"cell_type": None}


def estimate_ethnicity(state: State):
    """Function to estimate ethnicity from available data."""
    try:
        keys = get_ethnicity_keys(state["embeddings"], state["raw_keys"])
        if keys:
            ethnicity_value = state["attributes"].get(keys.pop())
            if ethnicity_value is not None:
                return {"ethnicity": str(ethnicity_value)}
        return {"ethnicity": None}
    except Exception:
        _error_tracker.record_row_error()
        return {"ethnicity": None}


def estimate_disease(state: State):
    """Function to estimate disease from available data."""
    try:
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
            try:
                llm = _get_llm()
                prompt = prompt_template.invoke(
                    {"sys_prompt": sys_prompt, "info": info_json}
                )
                structured_llm = llm.with_structured_output(DiseaseOutput)
                result = structured_llm.invoke(prompt)
                return {"disease": result["disease"] if result else None}  # type: ignore
            except Exception as llm_error:
                if _error_tracker.is_connection_error(llm_error):
                    _error_tracker.record_llm_connection_error()
                    _error_tracker.warn_connection_error_once()
                else:
                    _error_tracker.record_llm_inference_error()
                return {"disease": None}
        else:
            return {"disease": None}
    except Exception:
        _error_tracker.record_row_error()
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


def enrich_df(
    detailed_df: pd.DataFrame, basic_cols: list[str], enrich_backend: str
) -> pd.DataFrame:
    """Enrich a DataFrame with inferred biological metadata.

    Args:
        detailed_df: DataFrame containing sample metadata with attribute columns.
        basic_cols: List of basic column names to preserve in the output.

    Returns:
        DataFrame with enriched columns (age, sex, ethnicity, phenotype,
        cell_type, tissue, strain, disease).

    Raises:
        EnrichmentError: If a critical error occurs during enrichment.
        ModelLoadingError: If required models cannot be loaded.
    """
    # Reset error tracker for this enrichment run
    _error_tracker.reset()
    # Set the active backend so node functions can obtain the correct LLM
    global _llm_backend
    _llm_backend = enrich_backend

    if detailed_df.empty:
        _console.print(
            "[yellow]Warning[/yellow]  Empty DataFrame provided for enrichment"
        )
        for col in ENRICHED_COLS:
            detailed_df[col] = None
        existing_basic_cols = [col for col in basic_cols if col in detailed_df.columns]
        return detailed_df[existing_basic_cols + ENRICHED_COLS]

    attribute_cols = [col for col in detailed_df.columns if col not in basic_cols]

    if not attribute_cols:
        _console.print(
            "[yellow]Warning[/yellow]  No attribute columns found for enrichment"
        )
        for col in ENRICHED_COLS:
            detailed_df[col] = None
        existing_basic_cols = [col for col in basic_cols if col in detailed_df.columns]
        return detailed_df[existing_basic_cols + ENRICHED_COLS]

    try:
        refined_keys = get_refined_keys(attribute_cols)
        model = _get_embedding_model()
        key_embeddings = model.encode(refined_keys, convert_to_tensor=True)
    except ModelLoadingError:
        raise
    except Exception as e:
        raise EnrichmentError(f"Failed to compute key embeddings: {e}")

    # Initialize enriched columns with None
    for col in ENRICHED_COLS:
        detailed_df[col] = None

    _error_tracker.total_rows = len(detailed_df)

    for i, each_row in detailed_df[attribute_cols].iterrows():
        try:
            state = workflow.invoke(
                {
                    "attributes": each_row.to_dict(),
                    "embeddings": key_embeddings,
                    "raw_keys": attribute_cols,
                }  # type: ignore
            )
            for col in ENRICHED_COLS:
                detailed_df.loc[i, col] = state.get(col)
        except Exception:
            _error_tracker.record_row_error()
            # Continue with other rows, leaving this row's enriched columns as None
            continue

    # Show summary of any issues encountered
    _error_tracker.print_summary()

    existing_basic_cols = [col for col in basic_cols if col in detailed_df.columns]
    return detailed_df[existing_basic_cols + ENRICHED_COLS]

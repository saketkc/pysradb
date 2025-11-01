"""
Metadata enrichment for SRA/GEO datasets using LLMs and embeddings.
"""

import logging
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field
from tqdm.autonotebook import tqdm

logger = logging.getLogger(__name__)


def _prompt_install_enrichment_dependencies() -> bool:
    """
    Prompt user to install enrichment dependencies.

    Returns:
        True if installation succeeded, False otherwise.
    """
    try:
        response = (
            input(
                "Enrichment requires 'instructor' and 'pydantic'. Install now? (yes/no): "
            )
            .strip()
            .lower()
        )
    except (EOFError, KeyboardInterrupt):
        return False

    if response not in ["yes", "y"]:
        print("Install with: pip install 'pysradb[enrichment]'")
        return False

    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "instructor>=1.0.0",
                "pydantic>=2.0.0",
            ]
        )
        return True
    except subprocess.CalledProcessError:
        print(
            "Installation failed. Install manually with: pip install 'pysradb[enrichment]'"
        )
        return False


class MetadataExtractor(ABC):
    """Base class for metadata extraction from experiment descriptions."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract_metadata(
        self, text: str, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from text.

        Args:
            text: Input text (experiment description, title, etc.)
            fields: List of metadata fields to extract. If None, extract all.

        Returns:
            Dictionary with extracted metadata
        """
        pass

    def extract_batch(
        self, texts: List[str], fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract metadata from multiple texts.

        Args:
            texts: List of input texts
            fields: List of metadata fields to extract

        Returns:
            List of dictionaries with extracted metadata
        """
        return [self.extract_metadata(text, fields) for text in texts]

    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        text_column: Optional[str] = None,
        fields: Optional[List[str]] = None,
        prefix: str = "guessed_",
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """
        Enrich a DataFrame with extracted metadata.

        Args:
            df: Input DataFrame
            text_column: Column containing text to analyze. If None, combines sample text columns.
            fields: List of metadata fields to extract
            prefix: Prefix for new columns
            show_progress: Show progress bar (default: True)

        Returns:
            DataFrame with additional metadata columns
        """
        # If text_column not specified, combine all relevant columns
        if text_column is None:
            preferred_columns = [
                "sample_title",
                "experiment_title",
                "sample_source_name",
                "source_name",
                "sample_type",
                "sex",
                "age",
                "tissue",
                "cell_type",
                "disease",
                "treatment",
                "compound",
                "extract_protocol",
                "label_protocol",
                "sample_summary",
                "description",
            ]

            exclude_columns = [
                "study_title",
                "study_summary",
                "series_title",
                "series_summary",
            ]

            available_cols = []
            for col in preferred_columns:
                if col in df.columns and col not in exclude_columns:
                    available_cols.append(col)

            if not available_cols:
                raise ValueError(
                    "No suitable text columns found in DataFrame. "
                    "Please specify text_column parameter or ensure DataFrame "
                    "contains columns like 'sample_title', 'experiment_title', etc."
                )

            texts = []
            for idx, row in df.iterrows():
                parts = []
                for col in available_cols:
                    if pd.notna(row[col]):
                        parts.append(f"{col}: {row[col]}")
                texts.append(". ".join(parts))
        else:
            if text_column not in df.columns:
                raise ValueError(f"Column '{text_column}' not found in DataFrame")
            texts = df[text_column].fillna("").tolist()

        if show_progress:
            metadata_list = [
                self.extract_metadata(text, fields)
                for text in tqdm(texts, desc="Enriching metadata", unit="row")
            ]
        else:
            metadata_list = self.extract_batch(texts, fields)

        df_enriched = df.copy()
        for field in metadata_list[0].keys():
            df_enriched[f"{prefix}{field}"] = [m.get(field) for m in metadata_list]

        return df_enriched


class _MetadataExtraction(BaseModel):
    """Model for metadata extraction aligned with CellxGene schema.

    Fields are designed to match CellxGene Discover metadata structure and use
    ontology-based terms from UBERON (anatomy), MONDO (disease), and CL (cell types).

    Anatomical hierarchy: anatomical_system → organ → tissue
    """

    organ: str = Field(
        default="Unknown",
        description="High-level organ (e.g., brain, liver, heart, lung, breast)",
    )
    tissue: str = Field(
        default="Unknown", description="Specific tissue within organ (UBERON-based)"
    )
    anatomical_system: str = Field(
        default="Unknown",
        description="Body system (e.g., cardiovascular, nervous, immune)",
    )
    cell_type: str = Field(
        default="Unknown", description="Specific cell type (CL ontology-based)"
    )
    disease: str = Field(
        default="Unknown", description="Disease or condition (MONDO ontology-based)"
    )
    sex: str = Field(
        default="Unknown", description="Biological sex (male, female, mixed, Unknown)"
    )
    development_stage: str = Field(
        default="Unknown",
        description="Developmental stage (embryonic, fetal, adult, etc.)",
    )
    assay: str = Field(
        default="Unknown",
        description="Experimental assay type (RNA-seq, scRNA-seq, ATAC-seq, etc.)",
    )
    organism: str = Field(
        default="Unknown", description="Species (Homo sapiens, Mus musculus, etc.)"
    )


# DEFAULT_LLM_PROVIDER = "ollama/meditron"
DEFAULT_LLM_PROVIDER = "ollama/phi3"


def load_ontology_reference() -> Dict[str, List[str]]:
    """
    Returns comprehensive reference categories from UBERON, MONDO, and CL ontologies.

    Returns:
        Dictionary with ontology terms (organs, tissues, anatomical_systems, cell_types, diseases)
    """
    import json
    import os

    current_dir = os.path.dirname(__file__)
    ontology_path = os.path.join(current_dir, "ontology_reference.json")

    if not os.path.exists(ontology_path):
        raise FileNotFoundError(
            f"Ontology reference not found at {ontology_path}. "
            "Please ensure ontology_reference.json is in the pysradb package directory."
        )

    with open(ontology_path) as f:
        return json.load(f)


class LLMMetadataExtractor(MetadataExtractor):
    """Extract metadata using Large Language Models via Instructor."""

    def __init__(
        self,
        backend: str = DEFAULT_LLM_PROVIDER,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 3,
        **kwargs,
    ):
        super().__init__()
        self.provider = backend or DEFAULT_LLM_PROVIDER

        self.model = model

        env_key = self._provider_env_key()
        self.api_key = api_key or (os.getenv(env_key) if env_key else None)
        self.base_url = base_url
        self.temperature = temperature
        self.max_retries = max_retries
        self.kwargs = kwargs
        self.client = self._initialize_client()

    def _provider_env_key(self) -> Optional[str]:
        provider_name = self.provider.split("/")[0]
        if provider_name.lower() == "openai":
            return "OPENAI_API_KEY"
        if provider_name.lower() == "anthropic":
            return "ANTHROPIC_API_KEY"
        if provider_name.lower() == "google":
            return "GOOGLE_API_KEY"
        if provider_name.lower() == "mistral":
            return "MISTRAL_API_KEY"
        if provider_name.lower() == "groq":
            return "GROQ_API_KEY"
        return None

    def _initialize_client(self):
        try:
            import instructor
        except ImportError:
            if _prompt_install_enrichment_dependencies():
                import instructor
            else:
                raise ImportError(
                    "instructor package required. Install with: pip install 'pysradb[enrichment]'"
                )

        client_kwargs = self.kwargs.copy()
        if self.base_url:
            client_kwargs.setdefault("client_kwargs", {})
            client_kwargs["client_kwargs"].setdefault("base_url", self.base_url)

        provider_name = self.provider.split("/")[0].lower()
        if provider_name in ["ollama", "local"] and "mode" not in client_kwargs:
            client_kwargs["mode"] = instructor.Mode.JSON

        return instructor.from_provider(
            self.provider,
            api_key=self.api_key,
            **client_kwargs,
        )

    def _create_extraction_prompt(
        self, text: str, fields: Optional[List[str]] = None
    ) -> str:
        """Create prompt for metadata extraction."""
        default_fields = [
            "organ",
            "tissue",
            "anatomical_system",
            "cell_type",
            "disease",
            "sex",
            "development_stage",
            "assay",
            "organism",
        ]
        target_fields = fields or default_fields

        prompt = f"""Extract biological metadata using ontology-based terminology (UBERON, MONDO, CL).

CELL TYPE INFERENCE RULES (MOST IMPORTANT):
- Cell types indicate their origin organ/tissue. Use this biological knowledge:
  * Blood cells (PBMC, T cell, B cell, lymphocyte, monocyte, macrophage, NK cell) → organ: blood, tissue: peripheral blood, system: immune system
  * Brain cells (neuron, astrocyte, microglia, oligodendrocyte) → organ: brain, tissue: brain tissue, system: nervous system
  * Liver cells (hepatocyte) → organ: liver, tissue: liver parenchyma, system: digestive system
  * Heart cells (cardiomyocyte) → organ: heart, tissue: cardiac tissue, system: cardiovascular system
  * Lung cells (pneumocyte, alveolar cell) → organ: lung, tissue: lung parenchyma, system: respiratory system
  * Apply similar biological reasoning for other cell types

EXTRACTION RULES:
1. cell_type: Extract from metadata if mentioned. Lowercase.
2. organ: Look for explicit organ name OR infer from cell_type using biological knowledge above. Lowercase.
3. tissue: Look for explicit tissue OR infer from cell_type/organ using biological knowledge. Lowercase.
4. anatomical_system: Derive from organ/cell_type using biological knowledge (blood→immune, brain→nervous, liver→digestive, heart→cardiovascular, lung→respiratory). Lowercase.
5. disease: Extract ANY disease mentioned. "Normal"/"control"/"WT"→healthy. Lowercase.
6. sex: F=female, M=male. Return: male, female, mixed, or Unknown. Lowercase.
7. development_stage: From age - handle 'y' for years, 'm' for months (e.g., 17m=17 months=1.4 years). Use: 0-2y=infant, 3-12y=child, 13-18y=adolescent, 19-64y=adult, 65+=aged. Convert months to years when needed. Lowercase.
8. assay: RNA-seq, scRNA-seq, CITE-seq, ATAC-seq, etc.
9. organism: Homo sapiens, Mus musculus, or common names. Lowercase unless scientific.

EXAMPLES showing cell_type inference:
"cell_type: PBMC" → cell_type: pbmc, organ: blood, tissue: peripheral blood, anatomical_system: immune system
"cell_type: neuron" → cell_type: neuron, organ: brain, tissue: brain tissue, anatomical_system: nervous system
"cell_type: hepatocyte" → cell_type: hepatocyte, organ: liver, tissue: liver parenchyma, anatomical_system: digestive system

Metadata: {text}

Extract (use "Unknown" only if truly unclear):
"""
        field_descriptions = {
            "organ": "High-level organ (e.g., brain, liver, breast) (lowercase)",
            "tissue": "Specific tissue within organ, or 'Unknown' if not mentioned (lowercase)",
            "anatomical_system": "Major body system (lowercase)",
            "cell_type": "Specific cell type if mentioned (lowercase)",
            "disease": "Disease or condition - can be ANY disease, or 'healthy' for controls (lowercase)",
            "sex": "Biological sex: 'male', 'female', 'mixed', or 'Unknown'",
            "development_stage": "Life/developmental stage (lowercase)",
            "assay": "Sequencing or experimental assay type",
            "organism": "Species (scientific name preferred, or common name)",
        }

        for field in target_fields:
            if field in field_descriptions:
                prompt += f"- {field}: {field_descriptions[field]}\n"

        prompt += f"""
Respond in JSON format with these exact keys:
{{
  "organ": "your answer",
  "tissue": "your answer",
  "anatomical_system": "your answer",
  "cell_type": "your answer",
  "disease": "your answer",
  "sex": "your answer",
  "development_stage": "your answer",
  "assay": "your answer",
  "organism": "your answer"
}}"""

        return prompt

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call the LLM backend with the prompt."""
        try:
            create_kwargs = {
                "messages": [{"role": "user", "content": prompt}],
                "response_model": _MetadataExtraction,
                "temperature": self.temperature,
                "max_retries": self.max_retries,
            }

            if self.model is not None:
                create_kwargs["model"] = self.model

            response = self.client.chat.completions.create(**create_kwargs)
            return response.model_dump()
        except Exception as e:
            self.logger.error(f"LLM call failed for provider '{self.provider}': {e}")
            raise RuntimeError(
                f"LLM call failed with provider '{self.provider}': {e}"
            ) from e

    def extract_metadata(
        self, text: str, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from text using LLM.

        Args:
            text: Input text
            fields: List of fields to extract

        Returns:
            Dictionary with extracted metadata
        """
        if not text or text.strip() == "":
            return {
                "organ": "Unknown",
                "tissue": "Unknown",
                "anatomical_system": "Unknown",
                "cell_type": "Unknown",
                "disease": "Unknown",
                "sex": "Unknown",
                "development_stage": "Unknown",
                "assay": "Unknown",
                "organism": "Unknown",
            }

        prompt = self._create_extraction_prompt(text, fields)
        data = self._call_llm(prompt)

        if fields:
            return {field: data.get(field, "Unknown") for field in fields}

        return data


class EmbeddingMetadataExtractor(MetadataExtractor):
    """Extract metadata using embedding-based similarity matching."""

    def __init__(
        self,
        model_name: str = "FremyCompany/BioLORD-2023",
        backend: str = "sentence-transformers",
        reference_categories: Dict[str, List[str]] = None,
        **kwargs,
    ):
        """
        Initialize embedding-based metadata extractor.

        Args:
            model_name: Embedding model name (default: FremyCompany/BioLORD-2023 - optimized for biomedical text)
            backend: Embedding backend ("sentence-transformers", "fastembed")
            reference_categories: Reference categories for classification (required)
            **kwargs: Additional parameters for embedding model

        Raises:
            ValueError: If reference_categories is not provided
        """
        super().__init__()
        if reference_categories is None:
            raise ValueError(
                "reference_categories is required for embedding-based extraction. "
                "Please provide a dictionary mapping category names to lists of reference terms. "
                "Example: {'tissue': ['blood', 'brain', 'liver'], 'disease': ['healthy', 'cancer']}"
            )
        self.model_name = model_name
        self.backend = backend
        self.kwargs = kwargs
        self.model = self._load_model()
        self.reference_categories = reference_categories
        self.reference_embeddings = self._compute_reference_embeddings()

    def _load_model(self):
        """Load the embedding model."""
        if self.backend == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer

                return SentenceTransformer(self.model_name)
            except ImportError:
                if _prompt_install_enrichment_dependencies():
                    from sentence_transformers import SentenceTransformer

                    return SentenceTransformer(self.model_name)
                else:
                    raise ImportError(
                        "sentence-transformers required. Install with: pip install sentence-transformers"
                    )
        elif self.backend == "fastembed":
            try:
                from fastembed import TextEmbedding

                return TextEmbedding(model_name=self.model_name)
            except ImportError:
                if _prompt_install_enrichment_dependencies():
                    from fastembed import TextEmbedding

                    return TextEmbedding(model_name=self.model_name)
                else:
                    raise ImportError(
                        "fastembed required. Install with: pip install fastembed"
                    )
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _get_cache_path(self) -> str:
        """Get path for embedding cache file."""
        import hashlib
        import os
        from pathlib import Path

        cache_dir = Path.home() / ".cache" / "pysradb"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_key = f"{self.model_name}_{sorted(self.reference_categories.keys())}"
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()[:16]

        return str(cache_dir / f"embeddings_{cache_hash}.npz")

    def _compute_reference_embeddings(self) -> Dict[str, Any]:
        """Compute embeddings for reference categories with caching."""
        import os

        import numpy as np

        cache_path = self._get_cache_path()

        if os.path.exists(cache_path):
            try:
                cached = np.load(cache_path, allow_pickle=True)
                embeddings = {k: cached[k] for k in cached.files}
                self.logger.info(f"Loaded cached embeddings from {cache_path}")
                return embeddings
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")

        self.logger.info(
            f"Computing embeddings for {sum(len(v) for v in self.reference_categories.values())} terms..."
        )
        embeddings = {}
        for category, terms in self.reference_categories.items():
            if self.backend == "sentence-transformers":
                embeddings[category] = self.model.encode(terms, show_progress_bar=False)
            elif self.backend == "fastembed":
                embeddings[category] = np.array(list(self.model.embed(terms)))

        try:
            np.savez(cache_path, **embeddings)
            self.logger.info(f"Cached embeddings to {cache_path}")
        except Exception as e:
            self.logger.warning(f"Failed to cache embeddings: {e}")

        return embeddings

    def _find_best_match(
        self, text_embedding, category: str, threshold: float = 0.3
    ) -> str:
        """Find best matching category using cosine similarity."""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        if category not in self.reference_embeddings:
            return "Unknown"

        ref_embeddings = self.reference_embeddings[category]
        text_emb = np.array(text_embedding).reshape(1, -1)

        similarities = cosine_similarity(text_emb, ref_embeddings)[0]
        max_idx = np.argmax(similarities)
        max_sim = similarities[max_idx]

        if max_sim >= threshold:
            return self.reference_categories[category][max_idx]
        else:
            return "Unknown"

    def _parse_structured_fields(self, text: str) -> Dict[str, str]:
        """
        Parse structured text in 'field: value' format.

        Args:
            text: Input text with potential 'field: value' patterns

        Returns:
            Dictionary of parsed field-value pairs
        """
        import re

        parsed = {}
        # Pattern to match "field_name: value" where value extends to next field or end
        pattern = r"([a-z_]+):\s*([^.]+?)(?:\.|$)"
        matches = re.findall(pattern, text, re.IGNORECASE)

        for field_name, value in matches:
            parsed[field_name.strip().lower()] = value.strip()

        return parsed

    def _match_value_or_text(
        self, value: Optional[str], full_text: str, category: str
    ) -> str:
        """
        Match a specific extracted value or fall back to full text matching.

        This method first tries to match an extracted value (e.g., "F" from "sex: F")
        directly against reference categories. If that fails or no value is provided,
        it falls back to matching the full combined text.

        Args:
            value: Extracted field value (e.g., "F" from "sex: F")
            full_text: Full combined text for fallback matching
            category: Category name to match against

        Returns:
            Best matching category value or "Unknown"
        """
        import numpy as np

        # First try matching the extracted value directly if available
        if value and category in self.reference_categories:
            try:
                if self.backend == "sentence-transformers":
                    value_embedding = self.model.encode(value)
                elif self.backend == "fastembed":
                    value_embedding = np.array(list(self.model.embed([value])))[0]

                result = self._find_best_match(value_embedding, category)
                if result != "Unknown":
                    return result
            except Exception:
                pass  # Fall through to full text matching

        # Fall back to full text matching
        if category in self.reference_categories:
            try:
                if self.backend == "sentence-transformers":
                    text_embedding = self.model.encode(full_text)
                elif self.backend == "fastembed":
                    text_embedding = np.array(list(self.model.embed([full_text])))[0]

                return self._find_best_match(text_embedding, category)
            except Exception:
                return "Unknown"

        return "Unknown"

    def extract_metadata(
        self, text: str, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata using embedding similarity.

        Args:
            text: Input text
            fields: List of fields to extract

        Returns:
            Dictionary with extracted metadata
        """
        if not text or text.strip() == "":
            return {
                "organ": "Unknown",
                "tissue": "Unknown",
                "anatomical_system": "Unknown",
                "cell_type": "Unknown",
                "disease": "Unknown",
                "sex": "Unknown",
                "development_stage": "Unknown",
                "assay": "Unknown",
                "organism": "Unknown",
            }

        structured_fields = self._parse_structured_fields(text)

        organ = self._match_value_or_text(
            structured_fields.get("organ") or structured_fields.get("source_name"),
            text,
            "organs",
        )
        tissue = self._match_value_or_text(
            structured_fields.get("tissue"),
            text,
            "tissues",
        )
        cell_type = self._match_value_or_text(
            structured_fields.get("cell_type"), text, "cell_types"
        )
        disease = self._match_value_or_text(
            structured_fields.get("disease"), text, "diseases"
        )
        anatomical_system = self._match_value_or_text(
            structured_fields.get("anatomical_system"), text, "anatomical_systems"
        )
        sex = self._match_value_or_text(structured_fields.get("sex"), text, "sex")
        development_stage = self._match_value_or_text(
            structured_fields.get("age") or structured_fields.get("development_stage"),
            text,
            "development_stage",
        )
        assay = self._match_value_or_text(
            structured_fields.get("assay") or structured_fields.get("sample_title"),
            text,
            "assay",
        )
        organism = self._match_value_or_text(
            structured_fields.get("organism"), text, "organism"
        )

        return {
            "organ": organ,
            "tissue": tissue,
            "anatomical_system": anatomical_system,
            "cell_type": cell_type,
            "disease": disease,
            "sex": sex,
            "development_stage": development_stage,
            "assay": assay,
            "organism": organism,
        }


def create_metadata_extractor(
    method: str = "llm",
    backend: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> MetadataExtractor:
    """
    Factory function to create metadata extractor.

    Args:
        method: Extraction method (``llm`` or ``embedding``)
        backend: Backend for the method
        model: Model name
        kwargs: Additional parameters (as keyword arguments)

    Returns:
        MetadataExtractor instance

    Examples:
        >>> # LLM-based with Instructor (default provider)
        >>> extractor = create_metadata_extractor(method="llm")
        >>>
        >>> # Embedding-based (default: BioLORD-2023 for biomedical text)
        >>> extractor = create_metadata_extractor(method="embedding")
    """
    if method.lower() == "llm":
        backend = backend or DEFAULT_LLM_PROVIDER
        return LLMMetadataExtractor(backend=backend, model=model, **kwargs)
    elif method.lower() == "embedding":
        backend = backend or "sentence-transformers"
        return EmbeddingMetadataExtractor(
            model_name=model or "FremyCompany/BioLORD-2023",
            backend=backend,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown method: {method}. Choose 'llm' or 'embedding'")


def apply_dataframe_enrichment(
    df: pd.DataFrame,
    method: str = "embedding",
    backend: Optional[str] = None,
    model: Optional[str] = None,
    text_column: Optional[str] = None,
    show_progress: bool = True,
    prefix: str = "guessed_",
) -> pd.DataFrame:
    """
    Utility function to apply metadata enrichment to a DataFrame.

    This is a convenience function that handles:
    - Column auto-detection
    - Extractor initialization
    - Error handling
    - Progress display

    Args:
        df: Input DataFrame
        method: Enrichment method ('llm' or 'embedding')
        backend: Backend for the method
        model: Model name
        text_column: Column to use (auto-detected if None)
        show_progress: Show progress bar
        prefix: Prefix for new columns

    Returns:
        Enriched DataFrame

    Example:
        >>> from pysradb.metadata_enrichment import apply_dataframe_enrichment
        >>> enriched_df = apply_dataframe_enrichment(
        ...     df,
        ...     method="embedding",
        ...     text_column="experiment_title"
        ... )
    """
    if df is None or df.empty:
        return df

    try:
        extractor = create_metadata_extractor(
            method=method, backend=backend, model=model
        )

        if text_column is None:
            candidates = [
                "experiment_title",
                "experiment_desc",
                "study_title",
                "description",
                "sample_title",
                "source_name",
                "tissue",
                "condition",
                "treatment",
                "age",
                "sex",
                "strain",
            ]
            for candidate in candidates:
                if candidate in df.columns:
                    text_column = candidate
                    break

        if text_column and text_column in df.columns:
            return extractor.enrich_dataframe(
                df, text_column=text_column, prefix=prefix, show_progress=show_progress
            )
        else:
            logger.warning("No suitable text column found for enrichment")
            return df

    except ImportError as e:
        logger.warning(f"Enrichment dependencies not installed: {e}")
        return df
    except Exception as e:
        logger.warning(f"Enrichment failed: {e}")
        return df

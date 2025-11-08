"""
Llama.cpp-based metadata enrichment with confidence scoring.

This module provides metadata enrichment using llama-cpp-python with GGUF models,
adding confidence scores based on token log probabilities (NLL/PPL).
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from tqdm.autonotebook import tqdm

from .metadata_enrichment import MetadataExtractor, _MetadataExtraction

logger = logging.getLogger(__name__)


class LlamaCppMetadataExtractor(MetadataExtractor):
    """
    Extract metadata using llama-cpp-python with confidence scoring.

    This extractor uses llama-cpp-python to run local GGUF models and computes
    confidence scores for each extraction based on token log probabilities.
    """

    def __init__(
        self,
        model_id: str = "MoMonir/Llama3-OpenBioLLM-8B-GGUF",
        model_file: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,  # -1 = use all GPU layers
        **kwargs,
    ):
        """
        Initialize llama.cpp metadata extractor.

        Args:
            model_id: Hugging Face model ID (e.g., "MoMonir/Llama3-OpenBioLLM-8B-GGUF")
            model_file: Specific GGUF file to use (default: auto-detect Q4_K_M)
            temperature: Sampling temperature (default: 0.0 for deterministic)
            max_tokens: Maximum tokens to generate (default: 512)
            n_ctx: Context window size (default: 8192)
            n_gpu_layers: Number of layers to offload to GPU (-1 = all, default)
            **kwargs: Additional parameters for Llama
        """
        super().__init__()
        self.model_id = model_id
        self.model_file = model_file
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.kwargs = kwargs
        self.llm = self._initialize_model()

    def _check_llama_cpp_installed(self) -> bool:
        """Check if llama-cpp-python is installed."""
        try:
            import llama_cpp

            return True
        except ImportError:
            return False

    def _install_llama_cpp(self) -> bool:
        """Prompt user to install llama-cpp-python."""
        import subprocess

        try:
            response = (
                input(
                    "llama-cpp-python is required for this backend. Install now? (yes/no): "
                )
                .strip()
                .lower()
            )
        except (EOFError, KeyboardInterrupt):
            return False

        if response not in ["yes", "y"]:
            print(
                "Install with: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121"
            )
            return False

        try:
            # Install with CUDA support
            subprocess.check_call(
                [
                    "pip",
                    "install",
                    "llama-cpp-python",
                    "--extra-index-url",
                    "https://abetlen.github.io/llama-cpp-python/whl/cu121",
                ]
            )
            return True
        except subprocess.CalledProcessError:
            print(
                "Installation failed. Install manually with: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121"
            )
            return False

    def _download_model(self) -> str:
        """Download model from Hugging Face and return the GGUF file path."""
        from huggingface_hub import hf_hub_download

        logger.info(f"Downloading model: {self.model_id}")

        if self.model_file:
            model_path = hf_hub_download(
                repo_id=self.model_id, filename=self.model_file
            )
            logger.info(f"Downloaded model file: {model_path}")
            return model_path

        preferred_files = [
            "llama3-openbiollm-8b.Q4_K_M.gguf",
            "*Q4_K_M*.gguf",
            "*Q5_K_M*.gguf",
            "*Q4*.gguf",
            "*.gguf",
        ]

        from huggingface_hub import list_repo_files

        try:
            files = list_repo_files(repo_id=self.model_id)
            gguf_files = [f for f in files if f.endswith(".gguf")]

            if not gguf_files:
                raise RuntimeError(f"No GGUF files found in {self.model_id}")

            selected_file = None
            for preferred in preferred_files:
                if "*" in preferred:
                    pattern = preferred.replace("*", "")
                    matches = [f for f in gguf_files if pattern in f]
                    if matches:
                        selected_file = matches[0]
                        break
                else:
                    if preferred in gguf_files:
                        selected_file = preferred
                        break

            if not selected_file:
                selected_file = gguf_files[0]

            logger.info(f"Selected GGUF file: {selected_file}")
            model_path = hf_hub_download(repo_id=self.model_id, filename=selected_file)
            logger.info(f"Downloaded model: {model_path}")
            return model_path

        except Exception as e:
            raise RuntimeError(f"Failed to download model: {e}")

    def _initialize_model(self):
        """Initialize llama.cpp model."""
        if not self._check_llama_cpp_installed():
            if not self._install_llama_cpp():
                raise RuntimeError("llama-cpp-python is required but not installed")

        from llama_cpp import Llama

        model_path = self._download_model()

        logger.info(f"Loading model: {model_path}")
        logger.info(f"GPU layers: {self.n_gpu_layers}")

        llm = Llama(
            model_path=model_path,
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            logits_all=True,  # Need this for log probabilities
            verbose=False,
            **self.kwargs,
        )

        logger.info("Model loaded successfully")
        return llm

    def _create_extraction_prompt(
        self, metadata: str, fields: Optional[List[str]] = None
    ) -> str:
        """Create extraction prompt for the model."""
        if fields is None:
            fields = [
                "cell_type",
                "tissue",
                "disease",
                "organism",
                "developmental_stage",
            ]

        field_descriptions = {
            "cell_type": "the specific cell type or cell line used",
            "tissue": "the tissue or organ of origin",
            "disease": "any disease or condition being studied",
            "organism": "the organism or species",
            "developmental_stage": "the developmental stage or age",
            "treatment": "any treatments, drugs, or interventions applied",
            "assay": "the experimental assay or technique used",
        }

        fields_text = "\n".join(
            [f"- {field}: {field_descriptions.get(field, field)}" for field in fields]
        )

        prompt = f"""You are a bioinformatics expert. Extract the following information from the metadata below and return it as a JSON object.

Fields to extract:
{fields_text}

Metadata:
{metadata}

Return ONLY a valid JSON object with the extracted fields. Use null if information is not available. Do not include any other text.

JSON:"""

        return prompt

    def _compute_confidence_score(self, logprobs: List[float]) -> float:
        """
        Compute confidence score from log probabilities.

        Uses perplexity-based scoring:
        - Lower perplexity = higher confidence
        - Formula: confidence = 1 / (1 + perplexity / k) where k=10

        Args:
            logprobs: List of log probabilities for each token

        Returns:
            Confidence score between 0 and 1
        """
        if not logprobs or len(logprobs) == 0:
            return 0.5  # Default confidence when no logprobs

        # Compute mean negative log-likelihood
        mean_nll = -np.mean(logprobs)

        # Compute perplexity
        perplexity = np.exp(mean_nll)

        # Convert to confidence score (0-1 range)
        # Lower perplexity = higher confidence
        confidence = 1.0 / (1.0 + perplexity / 10.0)

        return float(confidence)

    def extract_metadata(
        self, text: str, fields: Optional[List[str]] = None
    ) -> _MetadataExtraction:
        """
        Extract metadata from text using llama.cpp.

        Args:
            text: Input text to extract metadata from
            fields: List of fields to extract

        Returns:
            _MetadataExtraction object with extracted data and confidence scores
        """
        prompt = self._create_extraction_prompt(text, fields)

        try:
            # Generate response with logprobs
            response = self.llm(
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                logprobs=1,  # Request log probabilities
                echo=False,
            )

            generated_text = response["choices"][0]["text"].strip()
            logprobs_data = response["choices"][0].get("logprobs", {})
            token_logprobs = logprobs_data.get("token_logprobs", [])
            valid_logprobs = [lp for lp in token_logprobs if lp is not None]
            confidence = self._compute_confidence_score(valid_logprobs)

            json_str = generated_text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            if "{" in json_str and "}" in json_str:
                start = json_str.find("{")
                end = json_str.rfind("}") + 1
                json_str = json_str[start:end]

            extracted_data = json.loads(json_str)

            field_confidences = {}
            for field in extracted_data.keys():
                if extracted_data[field] is not None:
                    field_confidences[f"{field}_confidence"] = confidence
                else:
                    field_confidences[f"{field}_confidence"] = 0.0

            return _MetadataExtraction(
                success=True,
                extracted_metadata=extracted_data,
                confidence_scores=field_confidences,
                error=None,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {generated_text}")
            return _MetadataExtraction(
                success=False,
                extracted_metadata={},
                confidence_scores={},
                error=f"JSON parsing error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return _MetadataExtraction(
                success=False,
                extracted_metadata={},
                confidence_scores={},
                error=str(e),
            )

    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = "sample_attribute",
        fields: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Enrich a DataFrame with extracted metadata.

        Args:
            df: Input DataFrame
            text_column: Column containing text to extract from
            fields: List of fields to extract

        Returns:
            DataFrame with added metadata columns
        """
        if fields is None:
            fields = [
                "cell_type",
                "tissue",
                "disease",
                "organism",
                "developmental_stage",
            ]

        enriched_df = df.copy()

        for field in fields:
            enriched_df[f"guessed_{field}"] = None
            enriched_df[f"guessed_{field}_confidence"] = None

        for idx, row in tqdm(
            enriched_df.iterrows(), total=len(enriched_df), desc="Enriching metadata"
        ):
            text = str(row[text_column]) if text_column in row else ""

            if not text or text == "nan":
                continue

            result = self.extract_metadata(text, fields)

            if result.success:
                for field in fields:
                    if field in result.extracted_metadata:
                        enriched_df.at[idx, f"guessed_{field}"] = (
                            result.extracted_metadata[field]
                        )

                for conf_field, conf_value in result.confidence_scores.items():
                    enriched_df.at[idx, f"guessed_{conf_field}"] = conf_value

        return enriched_df

    def __del__(self):
        """Cleanup llama.cpp model."""
        if hasattr(self, "llm") and self.llm is not None:
            del self.llm

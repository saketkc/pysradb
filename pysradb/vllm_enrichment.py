"""
vLLM-based metadata enrichment with confidence scoring.

This module provides metadata enrichment using vLLM with GGUF models,
adding confidence scores based on token log probabilities (NLL/PPL).
"""

import json
import logging
import os
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from tqdm.autonotebook import tqdm

from .metadata_enrichment import MetadataExtractor, _MetadataExtraction

logger = logging.getLogger(__name__)


class VLLMServerManager:
    """Manages vLLM server lifecycle for metadata enrichment."""

    def __init__(
        self,
        model_id: str,
        port: int = 8000,
        max_logprobs: int = 5,
        trust_remote_code: bool = True,
        gpu_memory_utilization: float = 0.4,
    ):
        """
        Initialize vLLM server manager.

        Args:
            model_id: Hugging Face model ID (e.g., "Qwen/Qwen2.5-1.5B-Instruct")
            port: Port for vLLM server (default: 8000)
            max_logprobs: Maximum logprobs to return (default: 5)
            trust_remote_code: Trust remote code for model loading
            gpu_memory_utilization: Fraction of GPU memory to use (default: 0.4)
        """
        self.model_id = model_id
        self.port = port
        self.max_logprobs = max_logprobs
        self.trust_remote_code = trust_remote_code
        self.gpu_memory_utilization = gpu_memory_utilization
        self.process = None
        self.base_url = f"http://localhost:{port}/v1"

    def _check_vllm_installed(self) -> bool:
        """Check if vLLM is installed."""
        try:
            import vllm

            return True
        except ImportError:
            return False

    def _install_vllm(self) -> bool:
        """Prompt user to install vLLM."""
        try:
            response = (
                input("vLLM is required for this backend. Install now? (yes/no): ")
                .strip()
                .lower()
            )
        except (EOFError, KeyboardInterrupt):
            return False

        if response not in ["yes", "y"]:
            print("Install with: pip install vllm")
            return False

        try:
            subprocess.check_call(
                [
                    "pip",
                    "install",
                    "vllm",
                ]
            )
            return True
        except subprocess.CalledProcessError:
            print("Installation failed. Install manually with: pip install vllm")
            return False

    def _download_model(self) -> str:
        """
        Download model from Hugging Face.

        Returns:
            Path to the downloaded model
        """
        try:
            from huggingface_hub import snapshot_download
        except ImportError:
            raise ImportError(
                "huggingface_hub is required for downloading models. "
                "Install with: pip install huggingface_hub"
            )

        logger.info(f"Downloading model {self.model_id}...")
        try:
            model_path = snapshot_download(
                repo_id=self.model_id,
                allow_patterns=[
                    "*.gguf",
                    "*.safetensors",
                    "*.bin",
                    "*.json",
                    "*.txt",
                    "*.model",
                    "tokenizer*",
                    "config.json",
                    "generation_config.json",
                ],
            )
            logger.info(f"Model downloaded to {model_path}")
            return model_path
        except Exception as e:
            raise RuntimeError(f"Failed to download model {self.model_id}: {e}")

    def _find_gguf_file(self, model_path: str) -> Optional[str]:
        """Find GGUF file in model directory."""
        import glob

        gguf_files = glob.glob(os.path.join(model_path, "*.gguf"))
        if not gguf_files:
            return None

        # Prefer Q4 or Q5 quantization for balance between speed and quality
        for preferred in ["Q4_K_M", "Q5_K_M", "Q4_K_S", "Q5_K_S"]:
            for gguf_file in gguf_files:
                if preferred in os.path.basename(gguf_file):
                    return gguf_file

        # Return first GGUF file if no preferred quantization found
        return gguf_files[0]

    def _get_tokenizer_path(self) -> str:
        """Get tokenizer path for the model."""
        # Map GGUF models to their base models for tokenizer
        tokenizer_mapping = {
            "MoMonir/Llama3-OpenBioLLM-8B-GGUF": "aaditya/Llama3-OpenBioLLM-8B",
            "Mungert/Qwen3-8B-GGUF": "Qwen/Qwen3-8B",
            "unsloth/Qwen3-8B-GGUF": "Qwen/Qwen3-8B",
        }

        return tokenizer_mapping.get(self.model_id, self.model_id)

    def start(self, max_retries: int = 3) -> bool:
        """
        Start vLLM server with automatic port retry on conflicts.

        Args:
            max_retries: Maximum number of port retries (default: 3)

        Returns:
            True if server started successfully
        """
        if not self._check_vllm_installed():
            if not self._install_vllm():
                raise RuntimeError("vLLM is required but not installed")

        # Check if port is already in use
        if self._is_server_running():
            logger.info(f"vLLM server already running on port {self.port}")
            return True

        model_path = self._download_model()
        gguf_file = self._find_gguf_file(model_path)

        if gguf_file:
            logger.info(f"Using GGUF file: {gguf_file}")
            model_arg = gguf_file
            tokenizer = self._get_tokenizer_path()
        else:
            logger.info(f"Using model ID directly (non-GGUF): {self.model_id}")
            model_arg = self.model_id
            tokenizer = None

        original_port = self.port
        for attempt in range(max_retries):
            current_port = original_port + attempt

            logger.info(
                f"Attempting to start vLLM server on port {current_port} (attempt {attempt + 1}/{max_retries})"
            )

            cmd = [
                "python",
                "-m",
                "vllm.entrypoints.openai.api_server",
                "--model",
                model_arg,
                "--port",
                str(current_port),
                "--max-logprobs",
                str(self.max_logprobs),
                "--gpu-memory-utilization",
                str(self.gpu_memory_utilization),
            ]

            if tokenizer:
                cmd.extend(["--tokenizer", tokenizer])

            if self.trust_remote_code:
                cmd.append("--trust-remote-code")

            # Add chat template to fix "default chat template is no longer allowed" error
            if (
                "llama" in self.model_id.lower()
                or "openbiollm" in self.model_id.lower()
            ):
                llama3_chat_template = (
                    "{% set loop_messages = messages %}"
                    "{% for message in loop_messages %}"
                    "{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>\\n\\n'+ message['content'] | trim + '<|eot_id|>' %}"
                    "{% if loop.index0 == 0 %}"
                    "{% set content = bos_token + content %}"
                    "{% endif %}"
                    "{{ content }}"
                    "{% endfor %}"
                    "{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' }}"
                )
                cmd.extend(["--chat-template", llama3_chat_template])
            elif "qwen" in self.model_id.lower():
                qwen_chat_template = (
                    "{% for message in messages %}"
                    "{% if loop.first and messages[0]['role'] != 'system' %}"
                    "{{ '<|im_start|>system\\nYou are a helpful assistant.<|im_end|>\\n' }}"
                    "{% endif %}"
                    "{{ '<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>\\n' }}"
                    "{% endfor %}"
                    "{{ '<|im_start|>assistant\\n' }}"
                )
                cmd.extend(["--chat-template", qwen_chat_template])

            logger.info(f"Starting vLLM server: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            logger.info("Waiting for vLLM server to start...")
            max_wait = 300
            start_time = time.time()

            while time.time() - start_time < max_wait:
                self.port = current_port
                self.base_url = f"http://localhost:{current_port}/v1"

                if self._is_server_running():
                    logger.info(f"vLLM server started successfully on port {self.port}")
                    return True

                if self.process.poll() is not None:
                    try:
                        stdout, stderr = self.process.communicate(timeout=5)
                    except:
                        logger.warning(
                            f"Process died on port {current_port}, but couldn't read output (timeout)"
                        )
                        stdout, stderr = "", ""

                    if stderr and (
                        "Address already in use" in stderr
                        or "OSError: [Errno 98]" in stderr
                    ):
                        logger.warning(
                            f"Port {current_port} is already in use, trying next port..."
                        )
                        break
                    elif stderr:
                        logger.error(
                            f"vLLM server failed to start.\nStdout: {stdout}\nStderr: {stderr}"
                        )
                        raise RuntimeError(
                            f"vLLM server failed with error: {stderr[:500]}"
                        )
                    else:
                        logger.warning(
                            f"Process died on port {current_port}, retrying..."
                        )
                        break

                time.sleep(2)

            if not self._is_server_running():
                stdout, stderr = "", ""

                if self.process and self.process.poll() is None:
                    logger.warning(
                        f"Server didn't start within timeout on port {current_port}"
                    )
                    self.process.kill()
                    try:
                        stdout, stderr = self.process.communicate(timeout=5)
                    except:
                        self.process.terminate()
                        try:
                            stdout, stderr = self.process.communicate(timeout=2)
                        except:
                            pass
                elif self.process:
                    try:
                        stdout, stderr = self.process.communicate(timeout=5)
                    except:
                        logger.warning(
                            f"Timed out reading process output on port {current_port}"
                        )
                        pass

                    if stderr:
                        logger.error(
                            f"vLLM server died during startup.\nStdout: {stdout[-1000:] if stdout else ''}\nStderr: {stderr[-1000:]}"
                        )

                    # Check for port conflict
                    if (
                        stderr
                        and "Address already in use" not in stderr
                        and "OSError: [Errno 98]" not in stderr
                    ):
                        # Not a port conflict - this is a real error
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Server failed on port {current_port}, trying next port..."
                            )
                        else:
                            raise RuntimeError(
                                f"vLLM server failed with error: {stderr[-500:]}"
                            )

                if attempt < max_retries - 1:
                    logger.info(f"Retrying with next port...")
                    continue
                else:
                    # Last attempt failed
                    logger.error(f"Failed to start server after {max_retries} attempts")
                    raise RuntimeError(
                        f"vLLM server failed to start within timeout after {max_retries} port attempts"
                    )

        # Should not reach here
        raise RuntimeError("vLLM server failed to start")

    def _is_server_running(self) -> bool:
        """Check if vLLM server is running."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def stop(self):
        """Stop vLLM server."""
        if self.process:
            logger.info("Stopping vLLM server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("vLLM server stopped")


class VLLMMetadataExtractor(MetadataExtractor):
    """
    Extract metadata using vLLM with confidence scoring.

    This extractor uses vLLM to run local LLMs with GGUF support and computes
    confidence scores for each extraction based on token log probabilities.
    """

    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
        port: int = 8000,
        temperature: float = 0.0,
        max_tokens: int = 512,
        auto_start_server: bool = True,
        **kwargs,
    ):
        """
        Initialize vLLM metadata extractor.

        Args:
            model_id: Hugging Face model ID (e.g., "Qwen/Qwen2.5-1.5B-Instruct")
            port: Port for vLLM server (default: 8000)
            temperature: Sampling temperature (default: 0.0 for deterministic)
            max_tokens: Maximum tokens to generate (default: 512)
            auto_start_server: Automatically start vLLM server if not running
            **kwargs: Additional parameters for server
        """
        super().__init__()
        self.model_id = model_id
        self.port = port
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = f"http://localhost:{port}/v1"
        self.served_model_name = model_id

        self.server_manager = VLLMServerManager(
            model_id=model_id,
            port=port,
            **kwargs,
        )

        if auto_start_server:
            self.server_manager.start()
            self.port = self.server_manager.port
            self.base_url = self.server_manager.base_url
            self.served_model_name = self._get_served_model_name()

    def _get_served_model_name(self) -> str:
        """
        Query vLLM server to get the actual model name it's serving.

        Returns:
            Model name as served by vLLM
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            response.raise_for_status()
            models_data = response.json()

            if models_data and "data" in models_data and len(models_data["data"]) > 0:
                served_name = models_data["data"][0]["id"]
                logger.info(f"vLLM is serving model as: {served_name}")
                return served_name
        except Exception as e:
            logger.warning(f"Could not get served model name from vLLM: {e}")

        return self.model_id

    def _create_extraction_prompt(
        self, text: str, fields: Optional[List[str]] = None
    ) -> str:
        """Create prompt for metadata extraction (reuse from LLMMetadataExtractor)."""
        from .metadata_enrichment import LLMMetadataExtractor

        # Reuse the prompt creation logic
        temp_extractor = LLMMetadataExtractor()
        return temp_extractor._create_extraction_prompt(text, fields)

    def _compute_confidence_score(self, logprobs: List[Dict[str, Any]]) -> float:
        """
        Compute confidence score from token logprobs.

        Uses mean negative log-likelihood (NLL) and converts to a 0-1 score.

        Args:
            logprobs: List of logprob dictionaries from vLLM

        Returns:
            Confidence score (0-1, higher is better)
        """
        if not logprobs:
            return 0.0

        # Extract log probabilities for the top token
        log_probs = []
        for token_logprob in logprobs:
            if token_logprob and "logprob" in token_logprob:
                log_probs.append(token_logprob["logprob"])

        if not log_probs:
            return 0.0

        # Compute mean NLL
        mean_nll = -np.mean(log_probs)

        # Convert to perplexity
        perplexity = np.exp(mean_nll)

        # Convert perplexity to 0-1 confidence score
        # Lower perplexity = higher confidence
        # Use sigmoid-like transformation: confidence = 1 / (1 + perplexity/k)
        # where k is a scaling factor (e.g., 10)
        k = 10.0
        confidence = 1.0 / (1.0 + perplexity / k)

        return float(confidence)

    def _call_vllm(self, prompt: str) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """
        Call vLLM API with the prompt.

        Returns:
            Tuple of (extracted_data, confidence_scores)
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.served_model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "logprobs": True,
                    "top_logprobs": 5,
                },
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logprobs = result["choices"][0].get("logprobs", {}).get("content", [])

            try:
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                else:
                    import re

                    json_match = re.search(r'\{[^}]*"organ"[^}]*\}', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)

                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {content[:500]}")
                raise RuntimeError(f"Failed to parse LLM response as JSON: {e}")

            overall_confidence = self._compute_confidence_score(logprobs)
            confidence_scores = {field: overall_confidence for field in data.keys()}

            return data, confidence_scores

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"vLLM API call failed: {e}")

    def extract_metadata(
        self, text: str, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from text using vLLM.

        Args:
            text: Input text
            fields: List of fields to extract

        Returns:
            Dictionary with extracted metadata and confidence scores
        """
        if not text or text.strip() == "":
            default_fields = {
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
            confidence_fields = {f"{k}_confidence": 0.0 for k in default_fields.keys()}
            return {**default_fields, **confidence_fields}

        prompt = self._create_extraction_prompt(text, fields)
        data, confidence_scores = self._call_vllm(prompt)

        # Add confidence scores to the result
        result = {}
        for field, value in data.items():
            result[field] = value
            result[f"{field}_confidence"] = confidence_scores.get(field, 0.0)

        return result

    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        text_column: Optional[str] = None,
        fields: Optional[List[str]] = None,
        prefix: str = "guessed_",
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """
        Enrich a DataFrame with extracted metadata and confidence scores.

        Args:
            df: Input DataFrame
            text_column: Column containing text to analyze
            fields: List of metadata fields to extract
            prefix: Prefix for new columns
            show_progress: Show progress bar

        Returns:
            DataFrame with additional metadata columns and confidence scores
        """
        # Reuse parent class logic for text column detection
        enriched_df = super().enrich_dataframe(
            df=df,
            text_column=text_column,
            fields=fields,
            prefix=prefix,
            show_progress=show_progress,
        )

        return enriched_df

    def close(self):
        """Close vLLM server."""
        self.server_manager.stop()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Enrichment Guide

This guide explains how to use metadata enrichment, how it behaves, and how to tune it.

## What Enrichment Does

Enrichment adds standardized biological attributes to metadata tables using an LLM.
The enriched columns are:

- `age`
- `sex`
- `ethnicity`
- `phenotype`
- `cell_type`
- `tissue`
- `strain`
- `disease`

When enrichment is enabled, these columns are added to the output table.

## CLI Usage

Enrich metadata for SRP or GSE accessions:

```bash
pysradb metadata SRP123456 --enrich
pysradb metadata GSE123456 --enrich
```

Choose the LLM backend:

```bash
pysradb metadata SRP123456 --enrich --model ollama/granite4:3b
pysradb metadata SRP123456 --enrich --model lmstudio/your-model
pysradb metadata SRP123456 --enrich --model vllm/your-model
```

Choose a different embedding model:

```bash
pysradb metadata SRP123456 --enrich --embed-model abhinand/MedEmbed-large-v0.1
```

## Important Behavior

- `--enrich` cannot be combined with `--detailed`. Enrichment uses the pysraweb API output and
  standardizes it before enrichment.
- If the input dataframe has more than 15 rows, you will be prompted to enrich all rows or just
  the first 15 for a quick review. More rows take longer to enrich.
- Enrichment runs in parallel across rows and shows a progress bar.
- A summary line is printed when enrichment finishes, showing the elapsed time.

## Programmatic Usage

If you are calling enrichment directly:

```python
from pysradb.enrichment import enrich_df

# detailed_df: dataframe with metadata
# basic_cols: list of columns considered "basic" (optional)
# enrichment_backend: LLM backend
# embedding_model: embedding model for key matching

enriched = enrich_df(
    detailed_df,
    basic_cols=[],
    enrichment_backend="ollama/granite4:3b",
    embedding_model="abhinand/MedEmbed-large-v0.1",
)
```

## Troubleshooting

- If enrichment is slow the first time, it may be loading models into memory.
- If the embedding model downloads every run, ensure your Hugging Face cache is persistent
  (for example, set `HF_HOME=~/.cache/huggingface`).

# llm_fetch

Clone HuggingFace model repositories, convert to GGUF format, and optionally quantize.

## Usage

```bash
llm_fetch <repo-url> [--quant_type Q4_K_M] [--model_dir /path]
```

## Model Directory

The model output directory is determined by (in order of priority):

1. `--model_dir` command-line flag
2. `ModelDir` in `llm_fetch.config.yaml`
3. Default: `~/.ai-scripts/llm_fetch/models`

The directory is created automatically if it doesn't exist.

To configure, copy the example config:

```bash
cp llm_fetch.example.yaml llm_fetch.config.yaml
```

Models are stored using the HuggingFace username as a parent directory:

```
<model_dir>/<username>/<reponame>/
```

## Dependencies

- Python 3.8+
- PyYAML
- llama.cpp (convert script and llama-quantize binary)

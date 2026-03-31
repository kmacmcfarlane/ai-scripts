# llm_fetch

Clone HuggingFace model repositories, convert to GGUF format, and optionally quantize for efficient inference.

## Usage

```bash
llm_fetch <repo-url> [--quant_type Q4_K_M] [--model_dir /path]
```

## Arguments

- `repo_url` (required): URL of the Hugging Face repository
- `--quant_type` (optional): Quantization type (e.g., Q4_K_M, Q5_K_M, Q8_0)
- `--model_dir` (optional): Directory to store models (overrides config file)

## How It Works

1. **Clone**: If the model doesn't exist locally, clones the repository
2. **Convert**: Converts the model to GGUF format (bf16) using llama.cpp's conversion script
3. **Quantize**: If a quantization type is specified, quantizes the bf16 GGUF file

The script skips steps if the output files already exist, making it safe to re-run.

## Configuration

Copy the example config to get started:

```bash
cp llm_fetch.example.yaml llm_fetch.config.yaml
```

The config file is gitignored so your local settings won't be committed.

### Model Directory

The model output directory is determined by (in order of priority):

1. `--model_dir` command-line flag
2. `ModelDir` in `llm_fetch.config.yaml`
3. Default: `~/.ai-scripts/llm_fetch/models`

The directory is created automatically if it doesn't exist.

Models are stored using the HuggingFace username as a parent directory:

```
<model_dir>/<username>/<reponame>/
```

### llama.cpp

Set `LlamaCppDir` in `llm_fetch.config.yaml` to point to your llama.cpp checkout:

```yaml
LlamaCppDir: ~/ai/repos/llama.cpp
```

When set, llm_fetch will:
- Resolve `convert_hf_to_gguf.py` and `llama-quantize` relative to that directory
- Activate a virtual environment if no `VIRTUAL_ENV` is already active, checking in order:
  1. `LlamaCppVirtualEnv` config value (explicit path to a venv)
  2. `.venv/` in the llama.cpp directory
  3. `venv/` in the llama.cpp directory

When not set, llm_fetch assumes `convert_hf_to_gguf.py` and `llama-quantize` are available in your PATH (e.g. via direnv or manual venv activation).

## Dependencies

- Python 3.8+
- Git
- PyYAML
- [llama.cpp](https://github.com/ggerganov/llama.cpp) (convert script and llama-quantize binary)

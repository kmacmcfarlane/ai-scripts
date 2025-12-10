# LLM Fetch & Quantize

A utility script to clone Hugging Face model repositories, convert them to GGUF format, and optionally quantize them for efficient inference.

## Features

- Clone Hugging Face model repositories
- Convert models to GGUF format (bf16)
- Optionally quantize models to various quantization levels
- Configurable model directory via YAML config file

## Prerequisites

- Python 3.x
- Git
- [llama.cpp](https://github.com/ggerganov/llama.cpp) installed and configured
- `llama-quantize` command available in PATH
- PyYAML package (`pip install pyyaml`)

## Configuration

Create a `llm_fetch.yaml` file in the script directory to override the default model directory (optional):

You can use `llm_fetch.example.yaml` as a template. If no configuration file is provided, models will be stored in `~/llm_models` by default.

**Note:** The `llm_fetch.yaml` file is gitignored, so your local configuration won't be committed to the repository.

## Usage

### Basic Usage

Clone and convert a model to GGUF format:

bash ./llm_fetch.sh [https://huggingface.co/username/model-name](https://huggingface.co/username/model-name)

### With Quantization

Clone, convert, and quantize a model:

bash ./llm_fetch.sh [https://huggingface.co/username/model-name](https://huggingface.co/username/model-name) --quant_type Q4_K_M


### Override Model Directory

Specify a custom model directory:

bash ./llm_fetch.sh [https://huggingface.co/username/model-name](https://huggingface.co/username/model-name) --model_dir /path/to/models


### Direct Python Execution

You can also run the Python script directly:

python3 llm_fetch.py https://huggingface.co/username/model-name --quant_type Q4_K_M

## Arguments

- `repo_url` (required): URL of the Hugging Face repository
- `--quant_type` (optional): Quantization type (e.g., Q4_K_M, Q5_K_M, Q8_0)
- `--model_dir` (optional): Directory to store models

## How It Works

1. **Clone**: If the model doesn't exist locally, it clones the repository
2. **Convert**: Converts the model to GGUF format (bf16) using llama.cpp's conversion script
3. **Quantize**: If a quantization type is specified, quantizes the bf16 GGUF file

The script skips steps if the output files already exist, making it safe to re-run.
# generate_rare_token

A command-line utility that finds rare single-token candidates in a model's vocabulary by measuring their distance from a common-token centroid in embedding space.

Tokens are scored by cosine similarity to a centroid built from common English words, punctuation, and digits. Tokens with the lowest similarity are considered "rare" — they occupy unusual regions of the embedding space.

Only tokens that are typeable (no whitespace, no control characters, not pure ASCII alphanumeric, max 10 chars) and round-trip to a single token ID are returned.

This tool is intended to be run via the `generate_rare_token.sh` wrapper (from your `PATH`), which automatically manages a local `.venv` and installs dependencies before executing the Python script.

## Prerequisites

- Python 3.8+
- `generate_rare_token.sh` available on your `PATH` (see repository-level PATH setup)

## Usage

Find rare tokens with the default model:
```bash
generate_rare_token.sh
```

Specify a custom model or number of results:
```bash
generate_rare_token.sh --model "Qwen/Qwen2.5-VL-7B-Instruct" -n 100
```

### Model argument

`--model` can be either:

- a Hugging Face model id (e.g. `Qwen/Qwen2.5-VL-7B-Instruct`), or
- a local path to a model directory.

## Arguments

- `--model` (optional): Pretrained model name or local path (default: Qwen/Qwen2.5-VL-7B-Instruct)
- `-n` (optional): Number of rare tokens to return (default: 50)

## Output

Each line contains the cosine similarity score, token ID, and token string:
```
-0.0312  id=12345   'ꜩ'
```

## Notes

- The first run for a remote model will take longer due to downloading model weights.
- Larger models require more memory since the full embedding matrix is loaded.
- Results depend on the model's tokenizer and embedding weights.

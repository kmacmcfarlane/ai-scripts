# token_embedding_search

A command-line utility that finds the nearest tokens in a model's embedding space to a given input text using cosine similarity.

This tool is intended to be run via the `token_embedding_search.sh` wrapper (from your `PATH`), which automatically manages a local `.venv` and installs dependencies before executing the Python script.

## Prerequisites

- Python 3.8+
- `token_embedding_search.sh` available on your `PATH` (see repository-level PATH setup)

## Usage

Find nearest tokens for a string:
```bash
token_embedding_search.sh "hello"
```

Specify a custom model or return more results with `--model` and `-k`:
```bash
token_embedding_search.sh --model "Qwen/Qwen2.5-VL-7B-Instruct" -k 50 "hello"
```

### Model argument

`--model` can be either:

- a Hugging Face model id (e.g. `Qwen/Qwen2.5-VL-7B-Instruct`), or
- a local path to a model directory.

## Arguments

- `--model` (required): Pretrained model name or local path
- `text` (required): Text to find nearest tokens for (quote it if it contains spaces)
- `-k` (optional): Number of nearest tokens to return (default: 20)

## Output

The tool prints:
- The token IDs for the input text
- The subtokens the input was split into
- The k nearest tokens with their cosine similarity scores

## Notes

- The first run for a remote model will take longer due to downloading model weights.
- Larger models require more memory since the full embedding matrix is loaded.
- Cosine similarity is used to measure closeness in embedding space.

   # token_count

A small command-line utility that prints the number of tokens in a piece of text for a given Hugging Face model/tokenizer.

This tool is intended to be run via the `token_count.sh` wrapper (from your `PATH`), which automatically manages a local `.venv` and installs dependencies before executing the Python script.

## Prerequisites

- Python 3.8+
- `token_count.sh` available on your `PATH` (see repository-level PATH setup)

## Usage

Count tokens for a string:
```bash
token_count.sh --model "Qwen/Qwen2.5-7B-Instruct" "Hello world!"
```

### Model argument

`--model` can be either:

- a Hugging Face model id (e.g. `Qwen/Qwen2.5-7B-Instruct`), or
- a local path to a tokenizer/model directory.

Example with a local path:

```shell
token_count.sh --model "./models/my-tokenizer" "Some text to measure"
```

## Arguments

- `--model` (required): Pretrained model name or local path
- `text` (required): Text to count tokens for (quote it if it contains spaces)

## Notes

- Tokenization is model-specific; the same text can produce different counts across models.
- The first run for a remote model may take longer due to downloading tokenizer files.
- This tool is designed for scripting/pipelines since it prints only the count.
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ai-scripts is a collection of independent Python CLI utilities for AI-related tasks. Each tool lives in its own directory with a corresponding bash wrapper in `bin/`.

## Architecture

- **Modular tools**: Each utility is self-contained in its own directory (no cross-imports between tools)
- **Wrapper pattern**: Shell scripts in `bin/` delegate to Python scripts, handling venv setup and path resolution
- **No shared library**: Tools are independent; they don't share code

### Tools

| Directory | Purpose |
|-----------|---------|
| `caption_util/` | Combine/split caption files for batch editing; rename files by extension |
| `llm_fetch/` | Clone HuggingFace models, convert to GGUF, optionally quantize (requires llama.cpp) |
| `token_count/` | Count tokens using HuggingFace tokenizers |
| `token_embedding_search/` | Find semantically similar tokens using model embeddings (cosine similarity) |
| `generate_rare_token/` | Find rare single-token candidates by distance from a common-token centroid |

## Running Tools

Tools are invoked via their shell wrappers (requires `bin/` on PATH):

```bash
caption_util.sh combine|split|rename [options]
llm_fetch.sh <repo-url> [--quant_type Q4_K_M] [--model_dir /path]
token_count.sh --model "model-id" "text"
token_embedding_search.sh --model "model-id" "text"
generate_rare_token.sh --model "model-id" -n 50
```

Or directly via Python:

```bash
python caption_util/caption_util.py combine|split|rename [options]
python llm_fetch/llm_fetch.py <repo-url> [options]
python token_count/token_count.py --model "model-id" "text"
python token_embedding_search/token_embedding_search.py --model "model-id" "text"
python generate_rare_token/generate_rare_token.py --model "model-id" -n 50
```

## Dependencies

- Python 3.8+
- Per-tool dependencies managed independently (e.g., `token_count/requirements.txt`)
- `token_count.sh` auto-creates and manages a `.venv` with hash-based dependency tracking
- `llm_fetch` requires external llama.cpp tools (convert script and llama-quantize binary)

## Build / Test / Lint

No build step, test framework, or linter is configured. Tools are run directly as scripts.

## Conventions

- CLI arguments use argparse with long flags (`--model`, `--input-dir`) and short flags where applicable
- Error output goes to stderr; normal output to stdout
- Exit code 0 for success, 1 for errors
- Subprocesses use list-based args (no shell=True) to avoid injection
- Config files use YAML (see `llm_fetch.example.yaml` as template; actual config is gitignored)
- Backup files are created automatically before overwriting (caption_util)

## Adding a New Tool

1. Create a directory with the tool's Python script
2. Add a shell wrapper in `bin/` following the existing pattern
3. If the tool has pip dependencies, add a `requirements.txt` and use venv management in the wrapper (see `bin/token_count.sh` for reference)

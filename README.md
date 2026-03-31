# ai-scripts
ai-scripts includes a collection of scripts for interacting with AI locally.

## Tools

| Tool | Description |
|------|-------------|
| [caption_util](caption_util/) | Combine/split caption files for batch editing; rename files by extension |
| [llm_fetch](llm_fetch/) | Clone HuggingFace models, convert to GGUF, optionally quantize |
| [token_count](token_count/) | Count tokens using HuggingFace tokenizers |
| [token_embedding_search](token_embedding_search/) | Find semantically similar tokens using model embeddings |
| [generate_rare_token](generate_rare_token/) | Find rare single-token candidates by distance from a common-token centroid |

## Prerequisites
- Python 3.8+

## PATH Setup
Add the ./bin directory to your PATH so the wrapper shell scripts can be called.
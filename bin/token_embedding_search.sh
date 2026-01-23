#!/bin/bash
set -euo pipefail

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

TOKEN_EMBEDDING_SEARCH_DIR="$DIR/../token_embedding_search"
VENV_DIR="$TOKEN_EMBEDDING_SEARCH_DIR/.venv"
REQ_FILE="$TOKEN_EMBEDDING_SEARCH_DIR/requirements.txt"
PY_SCRIPT="$TOKEN_EMBEDDING_SEARCH_DIR/token_embedding_search.py"

VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# Create venv if missing
if [[ ! -x "$VENV_PY" ]]; then
  # Deactivate any active virtual environment
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    deactivate
  fi
  echo "[token_embedding_search] Creating venv at: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# Install/refresh requirements when requirements.txt changes
REQ_HASH_FILE="$VENV_DIR/.requirements.sha256"
REQ_HASH="$(sha256sum "$REQ_FILE" | awk '{print $1}')"

if [[ ! -f "$REQ_HASH_FILE" ]] || [[ "$(cat "$REQ_HASH_FILE")" != "$REQ_HASH" ]]; then
  echo "[token_embedding_search] Installing requirements from: $REQ_FILE"
  "$VENV_PY" -m pip install --upgrade pip
  "$VENV_PIP" install -r "$REQ_FILE"
  echo "$REQ_HASH" > "$REQ_HASH_FILE"
fi

# Launch the python script with all arguments
"$VENV_PY" "$PY_SCRIPT" "$@"

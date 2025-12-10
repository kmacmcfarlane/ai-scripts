#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Launch the python script with all arguments
python3 "$DIR/../llm_fetch/llm_fetch.py" "$@"
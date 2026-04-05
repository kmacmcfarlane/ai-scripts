import argparse
import glob
import os
import subprocess
import sys
from pathlib import PurePosixPath
from urllib.parse import urlparse

import yaml
from huggingface_hub import hf_hub_download, snapshot_download


def parse_hf_url(url):
    """Parse a Hugging Face URL into repo_id, optional subdir, and optional filename.

    Supports formats:
        https://huggingface.co/user/repo
        https://huggingface.co/user/repo/tree/main/subdir
        https://huggingface.co/user/repo/blob/main/path/to/file.gguf
        https://huggingface.co/user/repo/resolve/main/file.gguf?download=true
        user/repo

    Returns:
        (repo_id, subdir, filename) where subdir and filename are mutually
        exclusive (at most one is set).
    """
    parsed = urlparse(url)

    # Bare repo_id (no scheme) — treat as user/repo or user/repo/subdir
    if not parsed.scheme:
        path = PurePosixPath(url.strip("/"))
        parts = path.parts
        if len(parts) == 2:
            return str(path), None, None
        if len(parts) > 2:
            return str(PurePosixPath(*parts[:2])), str(PurePosixPath(*parts[2:])), None
        raise ValueError(f"Cannot parse repo identifier: {url}")

    path = PurePosixPath(parsed.path.strip("/"))
    parts = path.parts

    if len(parts) < 2:
        raise ValueError(f"Cannot extract repo_id from URL: {url}")

    repo_id = str(PurePosixPath(*parts[:2]))
    rest = parts[2:]

    # No path type indicator — bare repo URL
    if len(rest) < 2:
        return repo_id, None, None

    path_type, _ref, *remainder = rest

    if not remainder:
        return repo_id, None, None

    tail = str(PurePosixPath(*remainder))

    if path_type in ("blob", "resolve"):
        return repo_id, None, tail

    if path_type == "tree":
        return repo_id, tail, None

    return repo_id, None, None


def download_repo(repo_id, output_dir, subdir=None):
    """Download a HuggingFace repo (or subdirectory) using snapshot_download."""
    kwargs = {
        "repo_id": repo_id,
        "local_dir": output_dir,
    }
    if subdir:
        kwargs["allow_patterns"] = f"{subdir}/**"

    print(f"Downloading {repo_id}" + (f" (subdir: {subdir})" if subdir else ""))
    snapshot_download(**kwargs)


def download_file(repo_id, filename, output_dir):
    """Download a single file from a HuggingFace repo using hf_hub_download."""
    print(f"Downloading {repo_id}/{filename}")
    hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=output_dir,
    )


def has_gguf_files(directory):
    """Check if directory contains any .gguf files."""
    return bool(glob.glob(os.path.join(directory, "**", "*.gguf"), recursive=True))


def find_llama_cpp_venv(llama_cpp_dir, venv_override):
    """Find the venv directory for llama.cpp.

    Checks LlamaCppVirtualEnv override first, then .venv/ and venv/ in llama_cpp_dir.
    Returns the path if found, None otherwise.
    """
    if venv_override:
        venv_override = os.path.expanduser(venv_override)
        if os.path.isdir(venv_override):
            return venv_override
        print(f"Warning: LlamaCppVirtualEnv does not exist: {venv_override}", file=sys.stderr)
        return None

    for candidate in [".venv", "venv"]:
        venv_dir = os.path.join(llama_cpp_dir, candidate)
        if os.path.isdir(venv_dir):
            return venv_dir
    return None


def setup_llama_cpp_env(llama_cpp_dir, venv_override=None):
    """Set up environment for llama.cpp tools.

    If llama_cpp_dir is provided, adds it to PATH and activates its venv
    if one exists and VIRTUAL_ENV isn't already set. If not provided, assumes
    tools are available in PATH.
    """
    if not llama_cpp_dir:
        return

    llama_cpp_dir = os.path.expanduser(llama_cpp_dir)
    if not os.path.isdir(llama_cpp_dir):
        print(f"Warning: LlamaCppDir does not exist: {llama_cpp_dir}", file=sys.stderr)
        return

    # Add llama.cpp dir to PATH so llama-quantize can be found
    os.environ["PATH"] = f"{llama_cpp_dir}:{os.environ['PATH']}"

    # Activate venv if no venv is already active
    if not os.environ.get("VIRTUAL_ENV"):
        venv_dir = find_llama_cpp_venv(llama_cpp_dir, venv_override)
        if venv_dir:
            os.environ["VIRTUAL_ENV"] = venv_dir
            os.environ["PATH"] = f"{os.path.join(venv_dir, 'bin')}:{os.environ['PATH']}"
            print(f"Activated venv: {venv_dir}")


def get_convert_script(llama_cpp_dir):
    """Return the path to convert_hf_to_gguf.py."""
    if llama_cpp_dir:
        return os.path.join(os.path.expanduser(llama_cpp_dir), "convert_hf_to_gguf.py")
    return "convert_hf_to_gguf.py"


def convert_to_gguf(output_dir, reponame, convert_script):
    """Convert a model to gguf format."""
    outfile = os.path.join(output_dir, f"{reponame}-bf16.gguf")
    if not os.path.exists(outfile):
        command = [
            "python",
            convert_script,
            "--outfile",
            outfile,
            "--outtype",
            "bf16",
            output_dir,
        ]
        subprocess.run(command, check=True)
        print(f"Converted model saved to: {outfile}")
    else:
        print(f"Skipping conversion to gguf, output file already exists: {outfile}")

def quantize_model(output_dir, reponame, quant_type):
    """Quantize a model."""
    bf16_file = os.path.join(output_dir, f"{reponame}-bf16.gguf")
    quantized_outfile = os.path.join(output_dir, f"{reponame}-{quant_type}.gguf")
    if not os.path.exists(quantized_outfile):
        command = [
            "llama-quantize",
            bf16_file,
            quantized_outfile,
            quant_type,
        ]
        subprocess.run(command, check=True)
        print(f"Quantized model saved to: {quantized_outfile}")
    else:
        print(f"Skipping quantization, output file already exists: {quantized_outfile}")


def read_config():
    """Read configuration from yaml file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "llm_fetch.config.yaml")
    if os.path.exists(config_path):
        print(f"Reading configuration from {config_path}")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        print(f"Configuration file {config_path} not found.")
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and quantize a model.",
        epilog="Model directory priority: --model_dir flag > ModelDir in llm_fetch.config.yaml > ~/.ai-scripts/llm_fetch/models. "
               "Models are stored as <model_dir>/<username>/<reponame>/. "
               "Copy llm_fetch.example.yaml to llm_fetch.config.yaml to configure."
    )
    parser.add_argument("repo_url", help="URL of the Hugging Face repository. Supports /tree/main/<subdir> for subdirectories and /blob/main/<file> for single files.")
    parser.add_argument(
        "--quant_type", nargs="?", default=None, help="Quantization type (optional)."
    )
    parser.add_argument(
        "--model_dir", help="Directory to store models. Overrides ModelDir from llm_fetch.config.yaml. Default: ~/.ai-scripts/llm_fetch/models"
    )
    parser.add_argument(
        "--skip-convert", action="store_true", default=False,
        help="Skip GGUF conversion. Auto-enabled when downloaded files are already in GGUF format."
    )
    args = parser.parse_args()

    config = read_config()

    config_version = config.get('Version')
    if config_version is not None and str(config_version) > "0.1":
        print(f"Configuration file version {config_version} is not supported by this script (max 0.1).", file=sys.stderr)
        sys.exit(1)

    # Parse the URL to get repo_id and optional subdir or filename
    repo_id, subdir, filename = parse_hf_url(args.repo_url)
    username, reponame = repo_id.split("/")

    # Set output directory
    default_dir = os.path.join(os.path.expanduser("~"), ".ai-scripts", "llm_fetch", "models")
    base_dir = args.model_dir or config.get('ModelDir', default_dir)
    base_dir = os.path.expanduser(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    print(f"Model Base Directory: {base_dir}")

    output_dir = os.path.join(base_dir, username, reponame)
    print(f"Output Directory: {output_dir}")

    # Download single file or full repository
    if filename:
        download_file(repo_id, filename, output_dir)
    else:
        download_repo(repo_id, output_dir, subdir=subdir)

    # Determine the effective working directory for conversion
    # When a subdir is fetched, it lives under output_dir/subdir
    effective_dir = os.path.join(output_dir, subdir) if subdir else output_dir

    # Auto-detect GGUF: skip conversion if files are already in GGUF format
    skip_convert = args.skip_convert
    if not skip_convert and has_gguf_files(effective_dir):
        print("Detected existing GGUF files, skipping conversion.")
        skip_convert = True

    # Set up llama.cpp environment
    llama_cpp_dir = config.get('LlamaCppDir')
    llama_cpp_venv = config.get('LlamaCppVirtualEnv')
    setup_llama_cpp_env(llama_cpp_dir, llama_cpp_venv)
    convert_script = get_convert_script(llama_cpp_dir)

    if not skip_convert:
        convert_to_gguf(effective_dir, reponame, convert_script)

    # Quantize if quantization type is provided
    if quant_type := args.quant_type:
        quantize_model(effective_dir, reponame, quant_type)

if __name__ == "__main__":
    main()

import argparse
import os
import subprocess
import sys

import yaml


def clone_repository(repo_url, output_dir):
    """Clone a repository to a specified directory."""
    if not os.path.exists(output_dir):
        command = ["git", "clone", "--progress", repo_url, output_dir]
        subprocess.run(command, check=True)

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
    parser.add_argument("repo_url", help="URL of the Hugging Face repository.")
    parser.add_argument(
        "--quant_type", nargs="?", default=None, help="Quantization type (optional)."
    )
    parser.add_argument(
        "--model_dir", help="Directory to store models. Overrides ModelDir from llm_fetch.config.yaml. Default: ~/.ai-scripts/llm_fetch/models"
    )
    args = parser.parse_args()

    repo_url = args.repo_url
    quant_type = args.quant_type
    config = read_config()

    if config.get('Version') > "0.1":
        print("Configuration file is unsupported by this script. config version: ", config.get('Version'), ", script version: 0.1")
        sys.exit(1)

    # Extract repository information from URL
    git_username = repo_url.split("/")[-2]
    reponame = repo_url.split("/")[-1]

    # Set output directory
    default_dir = os.path.join(os.path.expanduser("~"), ".ai-scripts", "llm_fetch", "models")
    base_dir = args.model_dir or config.get('ModelDir', default_dir)
    base_dir = os.path.expanduser(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    print(f"Model Base Directory: {base_dir}")


    output_dir = os.path.join(base_dir, git_username, reponame)
    print(f"Output Directory: {output_dir}")

    # Set up llama.cpp environment
    llama_cpp_dir = config.get('LlamaCppDir')
    llama_cpp_venv = config.get('LlamaCppVirtualEnv')
    setup_llama_cpp_env(llama_cpp_dir, llama_cpp_venv)
    convert_script = get_convert_script(llama_cpp_dir)

    # Clone repository if it doesn't exist
    if not os.path.exists(output_dir):
        clone_repository(repo_url, output_dir)

    # Convert to gguf
    convert_to_gguf(output_dir, reponame, convert_script)

    # Quantize if quantization type is provided
    if quant_type:
        quantize_model(output_dir, reponame, quant_type)

if __name__ == "__main__":
    main()


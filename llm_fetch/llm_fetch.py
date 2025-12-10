import argparse
import os
import subprocess
import sys

import yaml


def clone_repository(repo_url, output_dir):
    """Clone a repository to a specified directory."""
    if not os.path.exists(output_dir):
        command = ["git", "clone", repo_url, output_dir]
        subprocess.run(command, check=True)

def convert_to_gguf(output_dir, reponame):
    """Convert a model to gguf format."""
    outfile = os.path.join(output_dir, f"{reponame}-bf16.gguf")
    if not os.path.exists(outfile):
        command = [
            "python",
            "/home/rt/ai/repos/llama.cpp/convert_hf_to_gguf.py",
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
    parser = argparse.ArgumentParser(description="Fetch and quantize a model.")
    parser.add_argument("repo_url", help="URL of the Hugging Face repository.")
    parser.add_argument(
        "--quant_type", nargs="?", default=None, help="Quantization type (optional)."
    )
    parser.add_argument(
        "--model_dir", help="Directory to store models (optional)."
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
    base_dir = args.model_dir or config.get('ModelDir', os.path.join(os.path.expanduser("~"), "llm_models"))
    base_dir = os.path.expanduser(base_dir)
    os.makedirs(os.path.dirname(base_dir), exist_ok=True)
    print(f"Model Base Directory: {base_dir}")


    output_dir = os.path.join(base_dir, git_username, reponame)
    print(f"Output Directory: {output_dir}")

    # Clone repository if it doesn't exist
    if not os.path.exists(output_dir):
        clone_repository(repo_url, output_dir)

    # Activate the virtual environment
    os.environ["VIRTUAL_ENV"] = "/home/rt/ai/repos/llama.cpp/venv"
    os.environ["PATH"] = f"/home/rt/ai/repos/llama.cpp/venv/bin:{os.environ['PATH']}"

    # Convert to gguf
    convert_to_gguf(output_dir, reponame)

    # Quantize if quantization type is provided
    if quant_type:
        quantize_model(output_dir, reponame, quant_type)

if __name__ == "__main__":
    main()


from transformers import AutoTokenizer
import sys
import argparse

parser = argparse.ArgumentParser(description="Count tokens in text using a specified model")
parser.add_argument("--model", required=True, help="Pretrained model name or path (e.g. 'Qwen/Qwen2.5-7B-Instruct')")
parser.add_argument("text", help="Text to count tokens for")

if len(sys.argv) == 1 or any(arg in sys.argv for arg in ['--help', '-h', 'help']):
    parser.print_help()
    sys.exit(0)

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    parser.print_help()
    sys.exit(1)

tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)

ids = tok.encode(args.text)
print(len(ids))
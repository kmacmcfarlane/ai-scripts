import argparse
import re
import torch
from transformers import AutoTokenizer, AutoModel

COMMON_STRINGS = [
    "the", "a", "an", "and", "of", "to", "in", "on", "for", "with", "at", "by", "from",
    "is", "are", "was", "were", "be", "this", "that", "it",
    ",", ".", "-", "_",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "i", "rt", "ing",
]


def typeable(s):
    if not s:
        return False
    if any(ch.isspace() for ch in s):
        return False
    if "\ufffd" in s:
        return False
    if len(s) > 10:
        return False
    if re.fullmatch(r"[A-Za-z0-9]+", s):
        return False
    return True


def find_rare_tokens(tok, E, n=50):
    # normalize safely
    En = E / E.norm(dim=1, keepdim=True).clamp_min(1e-8)

    # build common-token centroid
    common_ids = []
    for s in COMMON_STRINGS:
        ids = tok.encode(s, add_special_tokens=False)
        if ids:
            common_ids.append(ids[0])
    common_ids = list(dict.fromkeys(common_ids))  # unique

    C = En[common_ids].mean(dim=0, keepdim=True)
    C = C / C.norm(dim=1, keepdim=True).clamp_min(1e-8)

    # score tokens by distance from common centroid
    sims = (En @ C.T).squeeze(1)

    # filter to typeable single-token candidates
    candidates = []
    V = En.shape[0]
    for i in range(V):
        s = tok.decode([i])
        if not typeable(s):
            continue
        enc = tok.encode(s, add_special_tokens=False)
        if len(enc) != 1 or enc[0] != i:
            continue
        candidates.append((float(sims[i]), i, s))

    # lowest similarity to common centroid first
    candidates.sort(key=lambda x: x[0])
    return candidates[:n]


def main():
    parser = argparse.ArgumentParser(
        description="Find rare single-token candidates by distance from a common-token centroid in embedding space."
    )
    parser.add_argument("--model", default="Qwen/Qwen2.5-VL-7B-Instruct",
                        help="Pretrained model name or local path (default: Qwen/Qwen2.5-VL-7B-Instruct)")
    parser.add_argument("-n", type=int, default=50,
                        help="Number of rare tokens to return (default: 50)")
    args = parser.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModel.from_pretrained(args.model, trust_remote_code=True, device_map="cpu")
    E = model.get_input_embeddings().weight.detach().float()

    candidates = find_rare_tokens(tok, E, n=args.n)
    for sim, i, s in candidates:
        print(f"{sim: .4f}  id={i:<6}  {repr(s)}")


if __name__ == "__main__":
    main()

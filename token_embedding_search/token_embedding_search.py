import argparse
import torch
from transformers import AutoTokenizer, AutoModel


def nearest_tokens(tok, E, text, k=20):
    ids = tok.encode(text, add_special_tokens=False)
    # average embedding across sub-tokens
    v = E[ids].mean(dim=0, keepdim=True)
    v = v / v.norm(dim=1, keepdim=True)
    En = E / E.norm(dim=1, keepdim=True)
    sims = (En @ v.T).squeeze(1)
    top = torch.topk(sims, k=k).indices.tolist()
    out = [(tok.decode([i]), float(sims[i])) for i in top]
    return ids, [tok.decode([i]) for i in ids], out


def main():
    parser = argparse.ArgumentParser(
        description="Find tokens nearest to input text in embedding space using cosine similarity."
    )
    parser.add_argument("text", help="Text to find nearest tokens for")
    parser.add_argument("--model", default="Qwen/Qwen2.5-VL-7B-Instruct",
                        help="Pretrained model name or local path (default: Qwen/Qwen2.5-VL-7B-Instruct)")
    parser.add_argument("-k", type=int, default=20, help="Number of nearest tokens to return (default: 20)")
    args = parser.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModel.from_pretrained(args.model, trust_remote_code=True)
    E = model.get_input_embeddings().weight.detach().float()

    ids, toks, nn, nan_count = nearest_tokens(tok, E, args.text, k=args.k)
    print("ids:", ids)
    print("subtokens:", toks)
    print("nan sims:", nan_count)
    print("nearest:")
    for t, s in nn:
        print(f"{s: .4f}  {repr(t)}")

def nearest_tokens(tok, E, text, k=20):
    # tokenize
    ids = tok.encode(text, add_special_tokens=False)

    # pre-normalize vocab embeddings safely
    Enorm = E.norm(dim=1, keepdim=True).clamp_min(1e-8)
    En = E / Enorm

    # build query vector from subtoken embeddings
    v = E[ids].mean(dim=0, keepdim=True)
    v = v / v.norm(dim=1, keepdim=True).clamp_min(1e-8)

    # cosine sims + NaN guard
    sims = (En @ v.T).squeeze(1)
    sims = torch.nan_to_num(sims, nan=-1e9, posinf=-1e9, neginf=-1e9)

    top = torch.topk(sims, k=k).indices.tolist()
    out = [(tok.decode([i]), float(sims[i])) for i in top]

    return ids, [tok.decode([i]) for i in ids], out, int(torch.isnan(sims).sum())


if __name__ == "__main__":
    main()
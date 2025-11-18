from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import argparse, math

def fmt(n):
    try:
        x = float(n)
        if math.isnan(x): return str(n)
        return f"{x:.0f}"
    except Exception:
        return str(n)

def parse_kv(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise SystemExit(f"Bad --f value '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def keep(meta, flt):
    return all(str((meta or {}).get(k)) == v for k, v in flt.items())

parser = argparse.ArgumentParser()
parser.add_argument("--store", required=True)
parser.add_argument("--query", required=True)
parser.add_argument("--f", action="append", default=[])
parser.add_argument("--item")
parser.add_argument("--site")
parser.add_argument("--source")
parser.add_argument("--k", type=int, default=8)
parser.add_argument("--kpool", type=int, default=64)
parser.add_argument("--aggregate", choices=["onhand","none"], default="none")
args = parser.parse_args()

flt = parse_kv(args.f)
if args.item:   flt["Item"]   = args.item
if args.site:   flt["Site"]   = args.site
if args.source: flt["Source"] = args.source

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = FAISS.load_local(args.store, embeddings=emb, allow_dangerous_deserialization=True)

# 1) embedding search (bigger pool), then post-filter
pairs = vs.similarity_search_with_score(args.query, k=max(args.kpool, args.k))
pairs = [(d,s) for (d,s) in pairs if not flt or keep(d.metadata, flt)]
pairs = pairs[:args.k]

# 2) FALLBACK: if nothing, do metadata-only scan (no embeddings)
if not pairs and flt:
    # scan all docs in the store and keep those matching filters
    all_docs = list(getattr(vs.docstore, "_dict", {}).values())
    matched = [d for d in all_docs if keep(getattr(d, "metadata", {}), flt)]
    # fake scores so output is uniform
    pairs = [(d, 0.0) for d in matched[:args.k]]

if not pairs:
    print("No results. Tip: relax filters or use a more specific query.")
else:
    for i, (doc, score) in enumerate(pairs, 1):
        print(f"\n#{i}  (score: {score:.4f})")
        print(doc.page_content[:300].strip())
        print("meta:", doc.metadata)

    if args.aggregate == "onhand":
        totals = {}
        for doc, _ in pairs:
            m = doc.metadata or {}
            sub = m.get("Secondary_ID") or "UNKNOWN"
            def to_float(x):
                try: return float(x)
                except Exception: return 0.0
            tq = to_float(m.get("Qty"))
            ta = to_float(m.get("Available_Qty"))
            tr = to_float(m.get("Reserved_Qty"))
            if sub not in totals:
                totals[sub] = {"Qty":0.0,"Available_Qty":0.0,"Reserved_Qty":0.0}
            totals[sub]["Qty"] += tq
            totals[sub]["Available_Qty"] += ta
            totals[sub]["Reserved_Qty"] += tr

        print("\n=== Aggregated by Subinventory (Secondary_ID) ===")
        print(f"{'Subinv':<16} {'Qty':>8} {'Avail':>8} {'Resvd':>8}")
        for sub, agg in sorted(totals.items()):
            print(f"{sub:<16} {fmt(agg['Qty']):>8} {fmt(agg['Available_Qty']):>8} {fmt(agg['Reserved_Qty']):>8}")

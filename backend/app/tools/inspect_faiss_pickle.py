# tools/inspect_faiss_pickle.py
import os, sys, pickle, json
from pathlib import Path

pkl_path = sys.argv[1] if len(sys.argv) > 1 else "rag_store/IR/faiss_index/index.pkl"
p = Path(pkl_path)
print(f"[INFO] Loading pickle: {p.resolve()}")

with open(p, "rb") as f:
    obj = pickle.load(f)

def safe_dir(x):
    try:
        return sorted(set(dir(x)))
    except Exception:
        return []

def maybe_keys(x):
    try:
        return list(x.keys())[:20]
    except Exception:
        return []

print(f"type(obj): {type(obj)}")
print(f"dir(obj) (subset): {safe_dir(obj)[:30]}")

if isinstance(obj, dict):
    print(f"dict keys (first 30): {maybe_keys(obj)}")
elif isinstance(obj, (list, tuple)):
    print(f"sequence length: {len(obj)}; types: {[type(i) for i in obj]}")
    # peek inside
    for i, it in enumerate(obj[:3]):
        print(f"  [{i}] type={type(it)} keys={maybe_keys(it)} dir_subset={safe_dir(it)[:15]}")
else:
    # Try attributes usually present
    for name in ["docstore", "index_to_docstore_id", "index_id_to_docstore_id", "faiss_index"]:
        has = hasattr(obj, name)
        print(f"hasattr(obj, {name!r}) -> {has}")

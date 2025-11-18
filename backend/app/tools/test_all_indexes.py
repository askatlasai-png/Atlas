# tools/test_all_indexes.py
import os, json, sys, numpy as np, pandas as pd
from validate_faiss_index import load_index_bundle, normalize_columns

INDEXES = {
    "ONHAND": "rag_store/ONHAND/faiss_index",
    "PO": "rag_store/PO/faiss_index",
    "SO": "rag_store/SO/faiss_index",
    "IR": "rag_store/IR/faiss_index",
    "LPN": "rag_store/LPN/faiss_index",
    "LPN_SERIAL": "rag_store/LPN_SERIAL/faiss_index",
    "LPN_SERIALS_AGG": "rag_store/LPN_SERIALS_AGG/faiss_index",
}

REQUIRED = {
    "ONHAND": ["item_id","location"],
    "PO": ["item_id","location","supplier","promised_date","ts"],
    "SO": ["item_id","location","customer","order_date","ts"],
    "IR": ["item_id","location","receipt_id","ts"],
    "LPN": ["lpn_id","item_id","location","ts"],
    "LPN_SERIAL": ["lpn_id","serial","item_id","location","ts"],
    "LPN_SERIALS_AGG": ["lpn_id","item_id","location","serial_count","ts"],
}

def _qty_col(df, cands):
    for c in cands:
        if c in df.columns: return c
    for c in df.columns:
        lc=c.lower()
        if any(t in lc for t in ["qty","quantity","onhand","available"]):
            return c
    return None

def agg_check(domain, df):
    if domain=="ONHAND":
        q=_qty_col(df, ["qty_onhand","onhand_qty","quantity"])
        return True if q is None else df.groupby("location")[q].sum().shape[0]>0
    if domain=="PO":
        return "promised_date" in df.columns and df["promised_date"].notna().any()
    if domain=="SO":
        return df["customer"].notna().mean()>=0.5 and df["location"].notna().mean()>=0.5
    if domain=="IR":
        return "receipt_id" in df.columns and df["receipt_id"].nunique()>0
    if domain=="LPN":
        return "lpn_id" in df.columns and df["lpn_id"].notna().mean()>0.9
    if domain=="LPN_SERIAL":
        return {"lpn_id","serial"}<=set(df.columns)
    if domain=="LPN_SERIALS_AGG":
        return "serial_count" in df.columns
    return True

def run(domain, path):
    if not os.path.exists(path):
        return {"domain":domain,"path":path,"status":"SKIP","problems":["path missing"]}
    idx, vecs, meta = load_index_bundle(path)
    meta = normalize_columns(meta, domain)
    probs=[]
    miss=[f for f in REQUIRED.get(domain,[]) if f not in meta.columns]
    if miss: probs.append(f"missing: {miss}")
    try:
        if not agg_check(domain, meta): probs.append("agg_check: FAIL")
    except Exception as e:
        probs.append(f"agg_check err: {e}")
    return {"domain":domain,"path":path,"rows":len(meta),"problems":probs,"status":"PASS" if not probs else "FAIL"}

if __name__=="__main__":
    report=[run(d,p) for d,p in INDEXES.items()]
    print("\n=== INDEX TEST MATRIX ===")
    for r in report:
        print(f"{r['domain']:18} : {r['status']}")
    print("=========================\n")
    print(json.dumps(report, indent=2))
    if any(r["status"]=="FAIL" for r in report if r["status"]!="SKIP"): sys.exit(1)

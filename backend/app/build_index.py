from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# -------------------------------------------------
# 1️⃣ Parse arguments
# -------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("--csv_path", required=True)
ap.add_argument("--out_dir", required=True)
ap.add_argument("--source", required=True)
ap.add_argument("--process_area", required=True)
args = ap.parse_args()

# -------------------------------------------------
# 2️⃣ Load metadata or CSV
# -------------------------------------------------
meta_path = Path(args.out_dir) / "meta.jsonl"
records = []

if meta_path.exists():
    print(f"🧾 Using metadata from {meta_path.resolve()}")
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
else:
    print(f"⚠️ No meta.jsonl found. Building directly from CSV.")
    df = pd.read_csv(args.csv_path).fillna("")
    for _, r in df.iterrows():
        records.append({
            "Source": args.source,
            "Process_Area": args.process_area,
            "Primary_ID": r.get("Primary_ID") or r.get("Item") or "",
            "Secondary_ID": r.get("Secondary_ID") or "",
            "Item": r.get("Item") or r.get("item_number") or "",
            "Qty": r.get("Qty") or r.get("onhand_qty") or "",
            "Available_Qty": r.get("Available_Qty") or r.get("available_qty") or "",
            "Reserved_Qty": r.get("Reserved_Qty") or r.get("reserved_qty") or "",
            "Context_Summary": r.get("Context_Summary") or "",
        })

def to_float_or_str(v):
    try:
        s = str(v).strip()
        if s == "": return ""
        return float(s)
    except Exception:
        return v

texts, metadatas = [], []
for rec in records:
    texts.append(rec.get("Context_Summary") or "")
    md = {
        "Source": rec.get("Source"),
        "Process_Area": rec.get("Process_Area"),
        "Item": rec.get("Item"),
        "Site": rec.get("Site") or rec.get("Org"),
        "Org": rec.get("Org"),
        "Secondary_ID": rec.get("Secondary_ID"),
        "Locator": rec.get("Locator"),
        "Month": rec.get("Month"),
        "SLA_Flag": rec.get("SLA_Flag"),
        "Status": rec.get("Status"),
        "Delivery_ID": rec.get("Delivery_ID"),
        "Tracking_Number": rec.get("Tracking_Number"),
        "Available_Qty": to_float_or_str(rec.get("Available_Qty")),
        "Reserved_Qty": to_float_or_str(rec.get("Reserved_Qty")),
        "Qty": to_float_or_str(rec.get("Qty")),
    }
    metadatas.append({k: v for k, v in md.items() if v not in ("", None)})

print(f"📊 Records loaded: {len(records)}")

# -------------------------------------------------
# 3️⃣ Build FAISS index
# -------------------------------------------------
emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = FAISS.from_texts(texts=texts, embedding=emb, metadatas=metadatas)

index_dir = Path(args.out_dir) / "faiss_index"
vs.save_local(str(index_dir))
print(f"✅ FAISS index saved to {index_dir.resolve()}")

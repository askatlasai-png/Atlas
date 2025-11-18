# tools/run_sample_queries_terminal.py
import os, pandas as pd
from validate_faiss_index import load_index_bundle, normalize_columns

DOMAINS = ["ONHAND","PO","SO","IR","LPN","LPN_SERIAL","LPN_SERIALS_AGG"]
BASE = "rag_store"

def _qty_col(df, prefs):
    for c in prefs:
        if c in df.columns: return c
    for c in df.columns:
        lc=c.lower()
        if any(t in lc for t in ["qty","quantity","onhand","available","count"]):
            return c
    return None

def print_head(title, df, n=8):
    print(f"\n🧩 {title}")
    if df is None or df.empty:
        print("   (no rows)")
    else:
        print(df.head(n).to_string(index=False))
        print(f"   ... {len(df)} total rows\n")

def onhand(df):
    q=_qty_col(df,["qty_onhand","onhand_qty","quantity"])
    if q and "location" in df.columns:
        by_loc=df.groupby("location")[q].sum().reset_index().sort_values(q,ascending=False)
        print_head("ONHAND: qty by location", by_loc)
    if {"item_id","location"}<=set(df.columns):
        by_item=df.groupby(["item_id","location"])[q].sum().reset_index().sort_values(q,ascending=False)
        print_head("ONHAND: item/location matrix", by_item)

def po(df):
    q=_qty_col(df,["promised_qty","ordered_qty","qty","quantity"])
    if "supplier" in df.columns:
        by_sup=df.groupby("supplier")[q].sum().reset_index().sort_values(q,ascending=False)
        print_head("PO: promised qty by supplier", by_sup)
    if "location" in df.columns:
        by_loc=df.groupby("location")[q].sum().reset_index().sort_values(q,ascending=False)
        print_head("PO: promised qty by location", by_loc)
    if "promised_date" in df.columns:
        print_head("PO: promised_date range", pd.DataFrame({
            "min_promised":[df["promised_date"].min()],
            "max_promised":[df["promised_date"].max()]
        }))

def so(df):
    if {"customer","location"}<=set(df.columns):
        by_cust=df.groupby(["customer","location"]).size().reset_index(name="so_lines").sort_values("so_lines",ascending=False)
        print_head("SO: customer/location activity", by_cust)
    if "order_date" in df.columns:
        by_day=df.groupby("order_date").size().reset_index(name="orders")
        print_head("SO: daily order counts", by_day)

def ir(df):
    if "receipt_id" in df.columns:
        by_receipt=df.groupby("receipt_id").size().reset_index(name="lines").sort_values("lines",ascending=False)
        print_head("IR: lines per receipt", by_receipt)
    if "location" in df.columns:
        by_loc=df.groupby("location").size().reset_index(name="receipts").sort_values("receipts",ascending=False)
        print_head("IR: receipts per location", by_loc)

def lpn(df):
    if {"lpn_id","location"}<=set(df.columns):
        by_loc=df.groupby("location")["lpn_id"].nunique().reset_index(name="unique_lpns").sort_values("unique_lpns",ascending=False)
        print_head("LPN: unique LPNs by location", by_loc)

def lpn_serial(df):
    if "lpn_id" in df.columns:
        by_lpn=df.groupby("lpn_id").size().reset_index(name="serials").sort_values("serials",ascending=False)
        print_head("LPN_SERIAL: serials per LPN", by_lpn)

def lpn_serials_agg(df):
    if {"lpn_id","serial_count"}<=set(df.columns):
        by_loc=df.groupby("location")["serial_count"].sum().reset_index().sort_values("serial_count",ascending=False)
        print_head("LPN_SERIALS_AGG: serial totals by location", by_loc)
        top=df.sort_values("serial_count",ascending=False)[["lpn_id","serial_count","location"]]
        print_head("LPN_SERIALS_AGG: top LPNs by serial_count", top)

RUNNERS={
    "ONHAND":onhand,"PO":po,"SO":so,"IR":ir,"LPN":lpn,"LPN_SERIAL":lpn_serial,"LPN_SERIALS_AGG":lpn_serials_agg
}

def main(item=None):
    print("\n=== DOMAIN SAMPLE SUMMARIES ===")
    for d in DOMAINS:
        path=os.path.join(BASE,d,"faiss_index")
        if not os.path.exists(path):
            print(f"\n⚠️  {d}: path missing"); continue
        _,_,meta=load_index_bundle(path)
        meta=normalize_columns(meta,d)
        if item and "item_id" in meta.columns:
            meta=meta[meta["item_id"].astype(str)==item]
        print(f"\n====== {d} ({len(meta)} rows) ======")
        RUNNERS[d](meta)
    print("\n=== END OF SUMMARIES ===\n")

if __name__=="__main__":
    main("ITEM-00004")

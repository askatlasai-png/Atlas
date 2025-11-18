# tools/run_sample_queries_terminal.py
# Terminal summaries for Atlas FAISS bundles (no CSV output).
# Prints small, readable aggregations per domain with robust fallbacks.

import os
import argparse
import pandas as pd
from validate_faiss_index import load_index_bundle, normalize_columns

DOMAINS = ["ONHAND", "PO", "SO", "IR", "LPN", "LPN_SERIAL", "LPN_SERIALS_AGG"]
BASE = "rag_store"

# -------- helpers --------
def _qty_col(df, prefs):
    """Pick a sensible quantity column if present; else None."""
    for c in prefs:
        if c in df.columns:
            return c
    for c in df.columns:
        lc = c.lower()
        if any(t in lc for t in ["qty", "quantity", "onhand", "available", "count"]):
            return c
    return None

def _print_head(title, df, n=10):
    print(f"\n🧩 {title}")
    if df is None or df.empty:
        print("   (no rows)")
        return
    # Reset index for pretty display, cap width by showing first n rows
    try:
        print(df.head(n).to_string(index=False))
    except Exception:
        # very wide frames: show columns + shape only
        print(f"   {list(df.columns)}")
        print(f"   {len(df)} rows")
    if len(df) > n:
        print(f"   ... {len(df)} total rows")

def _maybe_filter_item(df, item):
    if not item or "item_id" not in df.columns:
        return df
    return df[df["item_id"].astype(str) == item]

# -------- domain printers (each resilient to missing cols) --------
def show_onhand(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    q = _qty_col(df, ["qty_onhand", "onhand_qty", "quantity"])
    if "location" in df.columns:
        if q and q in df.columns:
            by_loc = df.groupby("location")[q].sum().reset_index().sort_values(q, ascending=False)
        else:
            by_loc = df.groupby("location").size().reset_index(name="rows").sort_values("rows", ascending=False)
        _print_head("ONHAND: by location", by_loc, topn)
    if {"item_id", "location"} <= set(df.columns):
        if q and q in df.columns:
            by_item_loc = (df.groupby(["item_id", "location"])[q]
                             .sum().reset_index().sort_values(q, ascending=False))
        else:
            by_item_loc = (df.groupby(["item_id", "location"])
                             .size().reset_index(name="rows").sort_values("rows", ascending=False))
        _print_head("ONHAND: item × location", by_item_loc, topn)

def show_po(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    q = _qty_col(df, ["promised_qty", "ordered_qty", "qty", "quantity"])
    if "supplier" in df.columns:
        if q and q in df.columns:
            by_sup = df.groupby("supplier")[q].sum().reset_index().sort_values(q, ascending=False)
        else:
            by_sup = df.groupby("supplier").size().reset_index(name="po_lines").sort_values("po_lines", ascending=False)
        _print_head("PO: by supplier", by_sup, topn)
    if "location" in df.columns:
        if q and q in df.columns:
            by_loc = df.groupby("location")[q].sum().reset_index().sort_values(q, ascending=False)
        else:
            by_loc = df.groupby("location").size().reset_index(name="po_lines").sort_values("po_lines", ascending=False)
        _print_head("PO: by location", by_loc, topn)
    if "promised_date" in df.columns and not df["promised_date"].dropna().empty:
        rng = pd.DataFrame({
            "min_promised": [df["promised_date"].min()],
            "max_promised": [df["promised_date"].max()]
        })
        _print_head("PO: promised_date range", rng, 5)

def show_so(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    if {"customer", "location"} <= set(df.columns):
        by_cust_loc = (df.groupby(["customer", "location"])
                         .size().reset_index(name="so_lines").sort_values("so_lines", ascending=False))
        _print_head("SO: customer × location", by_cust_loc, topn)
    if "order_date" in df.columns and not df["order_date"].dropna().empty:
        by_day = df.groupby("order_date").size().reset_index(name="orders").sort_values("order_date")
        _print_head("SO: daily orders", by_day, topn)

def show_ir(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    if "receipt_id" in df.columns:
        by_receipt = df.groupby("receipt_id").size().reset_index(name="lines").sort_values("lines", ascending=False)
        _print_head("IR: lines per receipt", by_receipt, topn)
    if "location" in df.columns:
        by_loc = df.groupby("location").size().reset_index(name="receipts").sort_values("receipts", ascending=False)
        _print_head("IR: receipts per location", by_loc, topn)

def show_lpn(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    if {"lpn_id", "location"} <= set(df.columns):
        by_loc = df.groupby("location")["lpn_id"].nunique().reset_index(name="unique_lpns").sort_values("unique_lpns", ascending=False)
        _print_head("LPN: unique LPNs by location", by_loc, topn)

def show_lpn_serial(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    if "lpn_id" in df.columns:
        by_lpn = df.groupby("lpn_id").size().reset_index(name="serials").sort_values("serials", ascending=False)
        _print_head("LPN_SERIAL: serials per LPN", by_lpn, topn)

def show_lpn_serials_agg(df, item=None, topn=10):
    df = _maybe_filter_item(df, item)
    if {"lpn_id", "serial_count"} <= set(df.columns):
        by_loc = (df.groupby("location")["serial_count"].sum()
                    .reset_index().sort_values("serial_count", ascending=False))
        _print_head("LPN_SERIALS_AGG: serial totals by location", by_loc, topn)
        top = df.sort_values("serial_count", ascending=False)[["lpn_id", "serial_count", "location"]]
        _print_head("LPN_SERIALS_AGG: top LPNs by serial_count", top, topn)

RUNNERS = {
    "ONHAND": show_onhand,
    "PO": show_po,
    "SO": show_so,
    "IR": show_ir,
    "LPN": show_lpn,
    "LPN_SERIAL": show_lpn_serial,
    "LPN_SERIALS_AGG": show_lpn_serials_agg,
}

# -------- main --------
def run_one(domain, base, item=None, topn=10):
    path = os.path.join(base, domain, "faiss_index")
    if not os.path.exists(path):
        print(f"\n⚠️  {domain}: path missing => {path}")
        return
    _, _, meta = load_index_bundle(path)
    meta = normalize_columns(meta, domain)
    print(f"\n====== {domain} ({len(meta)} rows) ======")
    RUNNERS[domain](meta, item=item, topn=topn)

def main():
    ap = argparse.ArgumentParser(description="Terminal summaries for Atlas FAISS bundles (no CSV).")
    ap.add_argument("--base", default=BASE, help="Base directory for rag_store")
    ap.add_argument("--item", default="ITEM-00004", help="Optional item filter (e.g., ITEM-00004)")
    ap.add_argument("--topn", type=int, default=10, help="Rows to display per summary")
    ap.add_argument("--domain", default="ALL",
                    help="Specific domain to show (ONHAND/PO/SO/IR/LPN/LPN_SERIAL/LPN_SERIALS_AGG) or ALL")
    args = ap.parse_args()

    print("\n=== DOMAIN SAMPLE SUMMARIES (terminal) ===")
    if args.domain.upper() == "ALL":
        for d in DOMAINS:
            run_one(d, args.base, item=args.item, topn=args.topn)
    else:
        d = args.domain.upper()
        if d not in DOMAINS:
            print(f"Unknown domain: {d}. Choose from: {', '.join(DOMAINS)}")
        else:
            run_one(d, args.base, item=args.item, topn=args.topn)
    print("\n=== END OF SUMMARIES ===\n")

if __name__ == "__main__":
    main()

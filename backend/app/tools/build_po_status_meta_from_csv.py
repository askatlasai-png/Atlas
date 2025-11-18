from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from datetime import datetime

def to_iso(s):
    if pd.isna(s) or str(s).strip() == "":
        return None
    try:
        return pd.to_datetime(s, errors="coerce").strftime("%Y-%m-%d")
    except Exception:
        return None

def days_between(start, end):
    try:
        if not start or not end:
            return None
        a = datetime.strptime(start, "%Y-%m-%d")
        b = datetime.strptime(end, "%Y-%m-%d")
        return (b - a).days
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to v_po_status_enriched.csv")
    ap.add_argument("--outdir", default="./rag_store/PO", help="Output folder")
    ap.add_argument("--process_area", default="Procurement", help="Default Process_Area if blank")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        raise SystemExit(f"❌ CSV not found: {csv_path.resolve()}")

    print(f"📦 Loading: {csv_path.resolve()}")
    df = pd.read_csv(csv_path).fillna("")

    lower = {c.lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            c = lower.get(n.lower())
            if c:
                return c
        return None

    cols = {
        "Primary_ID":      pick("po_number"),
        "Secondary_ID":    pick("line_location_id", "po_line_id"),
        "Actor":           pick("supplier_name", "vendor_name"),
        "Buyer_User_Id":   pick("buyer_user_id", "buyer_id", "buyer", "requested_by_user_id"),
        "Item":            pick("item_number", "item", "sku"),
        "Qty":             pick("quantity_ordered", "ordered_qty"),
        "Received_Qty":    pick("quantity_received", "received_qty"),
        "Promised_Date":   pick("promised_date"),
        "Need_By_Date":    pick("need_by_date", "needby_date"),
        "Actual_Date":     pick("delivered_date", "receipt_date"),
        "Status":          pick("po_status", "status"),
        "Site":            pick("ship_to_location", "warehouse"),
        "Org":             pick("organization_id", "org_code"),
        "Process_Area":    pick("Process_Area"),
        "SLA_Flag":        pick("SLA_Flag"),
        "Root_Cause_Tag":  pick("Root_Cause_Tag"),
        "Context_Summary": pick("Context_Summary")
    }

    if args.verbose:
        print("🧩 Column mapping used:")
        for k, v in cols.items():
            print(f"  {k:<15} ← {v}")

    lines = []
    for _, r in df.iterrows():
        md = {"Source": "PO", "Process_Area": args.process_area}

        # assign only non-empty values; keep defaults if blank/missing
        for dst, src in cols.items():
            if src:
                val = r.get(src, "")
                if str(val).strip() != "":
                    md[dst] = val

        # normalize dates
        md["Promised_Date"] = to_iso(md.get("Promised_Date"))
        md["Need_By_Date"]  = to_iso(md.get("Need_By_Date"))
        md["Actual_Date"]   = to_iso(md.get("Actual_Date"))
        md["Month"] = (md["Actual_Date"] or md["Promised_Date"] or md["Need_By_Date"] or "")[:7]

        # compute delay & SLA (Actual vs Promised)
        delay = days_between(md.get("Promised_Date"), md.get("Actual_Date"))
        if delay is not None:
            md["Delay_Days"] = delay
            md["SLA_Flag"] = "SLA_BREACH" if delay > 0 else "ON_TIME"
        else:
            md["SLA_Flag"] = md.get("SLA_Flag") or "UNKNOWN"

        # numeric quantities
        for q in ("Qty", "Received_Qty"):
            try:
                if md.get(q) not in ("", None):
                    md[q] = float(md[q])
            except Exception:
                pass

        lines.append(json.dumps(md, ensure_ascii=False))

    meta_path = out_dir / "meta.jsonl"
    meta_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Wrote {len(lines)} metadata rows → {meta_path.resolve()}")
    print(f"📂 Default Process_Area used for blanks: {args.process_area}")

if __name__ == "__main__":
    main()

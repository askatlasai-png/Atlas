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
    ap.add_argument("--csv", required=True, help="Path to v_so_delivery_status_enriched.csv")
    ap.add_argument("--outdir", default="./rag_store/SO", help="Output folder")
    ap.add_argument("--process_area", default="Sales", help="Default Process_Area if blank")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        raise SystemExit(f"❌ CSV not found: {csv_path.resolve()}")

    print(f"📦 Loading: {csv_path.resolve()}")
    df = pd.read_csv(csv_path).fillna("")

    # Case-insensitive header map
    lower = {c.lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            c = lower.get(n.lower())
            if c: return c
        return None

    cols = {
        "Primary_ID":          pick("so_number", "sales_order_number"),
        "Secondary_ID":        pick("so_line_id", "line_id"),
        "Delivery_ID":         pick("delivery_number", "shipment_number"),
        "Tracking_Number":     pick("tracking_number", "awb_number", "pro_number"),
        "Carrier":             pick("carrier_name", "shipper", "carrier"),
        "Ship_From":           pick("ship_from", "ship_from_site", "ship_from_location", "ship_from_location_id", "from_site"),
        "Ship_To":             pick("ship_to", "ship_to_site", "ship_to_location", "ship_to_location_id", "to_site"),
        "Customer_Or_Site_Name": pick("customer_or_site_name", "customer_name", "site_name"),
        "Ordered_By":          pick("ordered_by_user_id", "requested_by_user_id", "created_by", "ordered_by"),
        "Item":                pick("item_number", "item", "sku"),
        "Qty":                 pick("ordered_qty", "quantity_ordered"),
        "Shipped_Qty":         pick("shipped_qty", "quantity_shipped"),
        "Promised_Date":       pick("promised_date", "need_by_date"),
        "Actual_Date":         pick("shipped_date", "delivery_date", "actual_ship_date"),
        "Status":              pick("delivery_status", "status"),
        "Site":                pick("organization_id", "org_code"),
        "Org":                 pick("organization_id", "org_code"),
        "LPN_List":            pick("lpn_list", "lpn_numbers_csv", "lpns", "lpn_csv"),
        "Process_Area":        pick("Process_Area"),
        "SLA_Flag":            pick("SLA_Flag"),
        "Root_Cause_Tag":      pick("Root_Cause_Tag"),
        "Context_Summary":     pick("Context_Summary")
    }

    if args.verbose:
        print("🧩 Column mapping used:")
        for k, v in cols.items():
            print(f"  {k:<22} ← {v}")

    lines = []
    for _, r in df.iterrows():
        md = {"Source": "SO", "Process_Area": args.process_area}

        # assign only non-empty values (don't overwrite defaults with blanks)
        for dst, src in cols.items():
            if src:
                val = r.get(src, "")
                if str(val).strip() != "":
                    md[dst] = val

        # normalize dates + month
        md["Promised_Date"] = to_iso(md.get("Promised_Date"))
        md["Actual_Date"]   = to_iso(md.get("Actual_Date"))
        md["Month"] = (md["Actual_Date"] or md["Promised_Date"] or "")[:7]

        # compute delay & SLA
        delay = days_between(md.get("Promised_Date"), md.get("Actual_Date"))
        if delay is not None:
            md["Delay_Days"] = delay
            md["SLA_Flag"] = "SLA_BREACH" if delay > 0 else "ON_TIME"
        else:
            md["SLA_Flag"] = md.get("SLA_Flag") or "UNKNOWN"

        # numeric casts
        for q in ("Qty", "Shipped_Qty"):
            try:
                if md.get(q) != "":
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

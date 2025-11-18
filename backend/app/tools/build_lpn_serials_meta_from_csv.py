from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def to_iso(s):
    if pd.isna(s) or str(s).strip()=="":
        return None
    return pd.to_datetime(s, errors="coerce").strftime("%Y-%m-%d")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to v_lpn_serials_se_enriched.csv")
    ap.add_argument("--outdir", default="./rag_store/LPN_SERIAL", help="Output folder")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise SystemExit(f"❌ CSV not found: {csv_path.resolve()}")

    print(f"📦 Loading: {csv_path.resolve()}")
    df = pd.read_csv(csv_path).fillna("")

    # Case-insensitive column resolver
    lower = {c.lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            c = lower.get(n.lower())
            if c: return c
        return None

    cols = {
        "Primary_ID": pick("lpn_number", "lpn"),
        "Secondary_ID": pick("serial_number", "serial", "sn"),
        "Delivery_ID": pick("delivery_number", "delivery_id"),
        "Item": pick("item", "item_number", "sku"),
        "Qty": pick("quantity", "qty"),
        "Serials": pick("serial_number"),
        "Asset_Tags": pick("asset_tag", "asset_tags"),
        "Actor": pick("carrier_name", "supplier_name", "customer_name", "requested_by_user_id"),
        "Site": pick("warehouse", "site", "organization_id", "org_code"),
        "Org": pick("org_code", "organization_id"),
        "Promised_Date": pick("planned_ship_date", "promise_date", "planned_date"),
        "Actual_Date": pick("ship_confirm_date", "shipped_date", "creation_date", "last_update_date"),
        "Status": pick("serial_status", "status"),
        "Process_Area": pick("Process_Area"),
        "SLA_Flag": pick("SLA_Flag"),
        "Root_Cause_Tag": pick("Root_Cause_Tag"),
        "Context_Summary": pick("Context_Summary")
    }

    if args.verbose:
        print("Column mapping used:", cols)

    lines = []
    for _, r in df.iterrows():
        md = {
            "Source": "LPN_SERIAL",
            "Process_Area": "Logistics"
        }
        for dst, src in cols.items():
            md[dst] = r.get(src, "") if src else ""

        # Normalize dates + Month
        md["Promised_Date"] = to_iso(md.get("Promised_Date"))
        md["Actual_Date"]   = to_iso(md.get("Actual_Date"))
        md["Month"] = (md["Actual_Date"] or md["Promised_Date"] or "")[:7]
        md["SLA_Flag"] = md.get("SLA_Flag") or "UNKNOWN"

        # Cast quantity if present
        try:
            if md.get("Qty") != "":
                md["Qty"] = float(md["Qty"])
        except Exception:
            pass

        lines.append(json.dumps(md, ensure_ascii=False))

    meta_path = out_dir / "meta.jsonl"
    meta_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote {len(lines)} metadata rows → {meta_path.resolve()}")

if __name__ == "__main__":
    main()

from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def to_iso(s):
    if pd.isna(s) or str(s).strip() == "":
        return None
    return pd.to_datetime(s, errors="coerce").strftime("%Y-%m-%d")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to v_lpn_status_se_enriched.csv")
    ap.add_argument("--outdir", default="./rag_store/LPN", help="Output folder")
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
        "Primary_ID": pick("lpn_number", "lpn"),
        "Secondary_ID": pick("delivery_number"),
        "Delivery_ID": pick("delivery_id"),
        "Tracking_Number": pick("tracking_number"),
        "Item": pick("item", "item_number", "sku"),
        "Qty": pick("shipped_quantity", "requested_quantity"),
        "Actor": pick("carrier_name", "requested_by_user_id"),
        "Site": pick("organization_id", "warehouse", "site"),
        "Org": pick("organization_id", "org_code"),
        "Actual_Date": pick("creation_date"),
        "Status": pick("delivery_status"),
        "Process_Area": pick("Process_Area"),
        "SLA_Flag": pick("SLA_Flag"),
        "Root_Cause_Tag": pick("Root_Cause_Tag"),
        "Context_Summary": pick("Context_Summary")
    }

    if args.verbose:
        print("Column mapping used:", cols)

    lines = []
    for _, r in df.iterrows():
        md = {"Source": "LPN", "Process_Area": "Logistics"}
        for dst, src in cols.items():
            md[dst] = r.get(src, "") if src else ""

        md["Actual_Date"] = to_iso(md.get("Actual_Date"))
        md["Month"] = (md["Actual_Date"] or "")[:7]
        md["SLA_Flag"] = md.get("SLA_Flag") or "UNKNOWN"

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

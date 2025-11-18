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
    ap.add_argument("--csv", required=True, help="Path to v_lpn_serials_agg_se_enriched.csv")
    ap.add_argument("--outdir", default="./rag_store/LPN_SERIALS_AGG", help="Output folder")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise SystemExit(f"❌ CSV not found: {csv_path.resolve()}")

    print(f"📦 Loading: {csv_path.resolve()}")
    df = pd.read_csv(csv_path).fillna("")

    COLS = {
        "lpn_number": "Primary_ID",
        "delivery_number": "Secondary_ID",
        "serial_count": "Qty",
        "serials_csv": "Serials",
        "asset_tags": "Asset_Tags",
        "requested_by_user_id": "Actor",
        "creation_date": "Actual_Date",
        "Process_Area": "Process_Area",
        "SLA_Flag": "SLA_Flag",
        "Root_Cause_Tag": "Root_Cause_Tag",
        "Context_Summary": "Context_Summary"
    }

    lines = []
    for _, r in df.iterrows():
        md = {"Source": "LPN_SERIALS_AGG", "Process_Area": "Logistics"}
        for src, dst in COLS.items():
            md[dst] = r.get(src, "")

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

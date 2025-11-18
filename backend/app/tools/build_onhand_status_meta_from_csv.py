from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def to_iso(s):
    if pd.isna(s) or str(s).strip() == "":
        return None
    try:
        return pd.to_datetime(s, errors="coerce").strftime("%Y-%m-%d")
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to v_onhand_status_enriched.csv")
    ap.add_argument("--outdir", default="./rag_store/ONHAND", help="Output folder")
    ap.add_argument("--process_area", default="Inventory", help="Default Process_Area if blank")
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
        "Primary_ID":    pick("item_number", "item", "sku", "item"),
        "Secondary_ID":  pick("subinventory_code", "subinventory", "subinv"),
        "Item":          pick("item_number", "item", "sku", "item"),
        "Qty":           pick("onhand_qty", "quantity_onhand", "on_hand_quantity"),
        "Available_Qty": pick("available_qty", "available_quantity"),
        "Reserved_Qty":  pick("reserved_qty", "reserved_quantity"),
        "Locator":       pick("locator_code", "locator", "location_code"),
        "Site":          pick("organization_id", "org_code", "warehouse"),
        "Org":           pick("organization_id", "org_code", "warehouse"),
        "Actual_Date":   pick("last_update_date", "creation_date"),
        "Status":        pick("onhand_status", "status"),
        "Process_Area":  pick("Process_Area"),
        "SLA_Flag":      pick("SLA_Flag"),
        "Root_Cause_Tag":pick("Root_Cause_Tag"),
        "Context_Summary": pick("Context_Summary")
    }

    if args.verbose:
        print("🧩 Column mapping used:")
        for k, v in cols.items():
            print(f"  {k:<15} ← {v}")

    lines = []
    for _, r in df.iterrows():
        md = {"Source": "ONHAND", "Process_Area": args.process_area}

        # assign only non-empty values; don't clobber defaults
        for dst, src in cols.items():
            if src:
                val = r.get(src, "")
                if str(val).strip() != "":
                    md[dst] = val

        # normalize date + Month
        md["Actual_Date"] = to_iso(md.get("Actual_Date"))
        md["Month"] = (md["Actual_Date"] or "")[:7]
        md["SLA_Flag"] = md.get("SLA_Flag") or "UNKNOWN"
        md["Status"] = md.get("Status") or "ONHAND"

        # numeric conversions
        for q in ("Qty", "Available_Qty", "Reserved_Qty"):
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

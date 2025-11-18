from __future__ import annotations
import pandas as pd, json
from pathlib import Path
from datetime import datetime

IN_CSV  = "idx_v_ir_status_enriched/v_ir_status_enriched.csv"   # adjust if needed
OUT_DIR = Path("./rag_store/IR")

# Columns that exist in your CSV (as you uploaded)
COLS = {
    "requisition_number": "Primary_ID",
    "requisition_line_id": "Secondary_ID",
    "requested_by_user_id": "Actor",
    "item": "Item",
    "quantity": "Qty",
    "organization_id": "Site",
    "need_by_date": "Promised_Date",
    "creation_date": "Actual_Date",   # best available proxy
    "req_status": "Status",
    "Process_Area": "Process_Area",
    "SLA_Flag": "SLA_Flag",
    "Context_Summary": "Context_Summary",  # already present; will be embedded elsewhere
}

def to_iso(s):
    if pd.isna(s) or str(s).strip()=="":
        return None
    try:
        return pd.to_datetime(s, errors="coerce").strftime("%Y-%m-%d")
    except Exception:
        return None

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_CSV).fillna("")

    lines = []
    for _, r in df.iterrows():
        md = {"Source": "IR", "Org": None}  # Org not explicit here
        for src, dst in COLS.items():
            val = r.get(src, "")
            md[dst] = val

        # normalize dates + Month
        md["Promised_Date"] = to_iso(md.get("Promised_Date"))
        md["Actual_Date"]   = to_iso(md.get("Actual_Date"))
        # No reliable delay here (no received_date), so we won’t compute Delay_Days
        md["Month"] = (md["Actual_Date"] or md["Promised_Date"] or "")[:7]
        # Ensure Process_Area present, default if missing
        md["Process_Area"] = md.get("Process_Area") or "Receiving"
        # Default SLA_Flag if blank
        md["SLA_Flag"] = md.get("SLA_Flag") or "UNKNOWN"

        lines.append(json.dumps(md, ensure_ascii=False))

    (OUT_DIR / "meta.jsonl").write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote {len(lines)} IR metadata rows to {OUT_DIR/'meta.jsonl'}")

if __name__ == "__main__":
    main()

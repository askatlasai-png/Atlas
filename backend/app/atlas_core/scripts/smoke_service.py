# scripts/smoke_service.py
from atlas_service import run_query

CASES = [
  'Compare PO vs onhand for ITEM-00004 at "WH1"',
  'SO delivery status for customer "Acme Retail" at WH1',
  'IR receipts summary between 2025-10-01 and 2025-10-31',
  'Just show me stuff for ITEM-00004 at DC-ATL'
]

if __name__ == "__main__":
    print("[SMOKE] Router + Executor")
    for q in CASES:
        out = run_query(q, k=4, mode="HYBRID")
        print("\nQ:", q)
        print("intent:", out["meta"]["plan_intent"])
        print("why   :", out["meta"]["plan_rationale"])
        print("lineage:")
        for step in out["meta"]["lineage"]:
            print(" ", step)
        print("rows:", len(out["rows"]))

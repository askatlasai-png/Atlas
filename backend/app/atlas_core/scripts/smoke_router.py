# scripts/smoke_router.py
# Smoke test for AtlasQueryRouter (no executor)
# Works on Windows/PowerShell and POSIX shells.

import os
import sys
from pathlib import Path

# --- Make sure Python can find atlas_query_router.py ---
HERE = Path(__file__).resolve()
ATLAS_CORE_DIR = HERE.parents[1]          # .../atlas_core
if str(ATLAS_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(ATLAS_CORE_DIR))

# Try both import styles (package vs. flat file)
try:
    from atlas_core.atlas_query_router import route_query   # if atlas_core is a package
except Exception:
    from atlas_query_router import route_query               # if running inside atlas_core

# --------------- Test cases ---------------
CASES = [
    'Compare PO vs onhand for ITEM-00004 at "WH1"',
    'SO delivery status for customer "Acme Retail" at WH1',
    'IR receipts summary between 2025-10-01 and 2025-10-31',
    'Just show me stuff for ITEM-00004 at DC-ATL'
]

def main():
    mode = os.getenv("ATLAS_ROUTER_MODE")  # HYBRID | LOCAL_ONLY | OPENAI_ONLY (if None, router uses default)
    try:
        k = int(os.getenv("ATLAS_DEFAULT_K", "4"))
    except ValueError:
        k = 4

    print("[SMOKE] Router only (mode:", mode or "router-default", ", k:", k, ")")

    for q in CASES:
        print("\nQ:", q)
        plan = route_query(q, k=k, mode=mode)  # pass env-mode through; router will fall back to default if None
        print("Intent:", plan.intent)
        print("Rationale:", plan.rationale)
        for s in plan.steps:
            print("  ", s)

if __name__ == "__main__":
    main()

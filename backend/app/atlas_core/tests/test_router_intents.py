import os
from atlas_core.atlas_query_router import route_query
from atlas_core.atlas_query_router import route_query
from atlas_core.atlas_service import run_query


def _set(mode, tau_local="0.60"):
    os.environ["ATLAS_ROUTER_MODE"] = mode
    os.environ["ATLAS_TAU_LOCAL"] = tau_local

def test_local_only_core_cases():
    _set("LOCAL_ONLY", "0.55")
    q1 = 'Compare PO vs onhand for ITEM-00004 at "WH1"'
    q2 = 'SO delivery status for customer "Acme Retail" at WH1'
    q3 = 'IR receipts summary between 2025-10-01 and 2025-10-31'
    q4 = 'Just show me stuff for ITEM-00004 at DC-ATL'

    assert route_query(q1).intent == "po_vs_onhand"
    assert route_query(q2).intent == "so_delivery_status"
    assert route_query(q3).intent == "ir_receipts_summary"
    assert route_query(q4).intent in {"onhand_by_item","generic_safe_explore"}

def test_hybrid_never_empty_plan(monkeypatch):
    _set("HYBRID", "0.60")
    out = route_query('SO delivery status for "Acme Retail" at WH1', k=4)
    assert out.intent in {"so_delivery_status","generic_safe_explore"}
    assert len(out.steps) >= 2

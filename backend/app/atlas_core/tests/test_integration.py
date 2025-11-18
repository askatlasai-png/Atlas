import os
from atlas_core.atlas_service import run_query

def test_hybrid_never_empty_plan():
    os.environ["ATLAS_ROUTER_MODE"] = "HYBRID"
    os.environ["ATLAS_TAU_LOCAL"] = "0.60"
    out = run_query('SO delivery status for "Acme Retail" at WH1', k=4)
    assert out["meta"]["plan_intent"] in {"so_delivery_status", "generic_safe_explore"}
    assert len(out["meta"]["lineage"]) >= 1

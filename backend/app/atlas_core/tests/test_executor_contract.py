from atlas_core.atlas_service import run_query
from atlas_core.atlas_query_router import route_query
from atlas_core.atlas_service import run_query


def test_executor_lineage_present():
    out = run_query('IR receipts summary between 2025-10-01 and 2025-10-31', k=4, mode="LOCAL_ONLY")
    meta = out["meta"]
    assert isinstance(meta["lineage"], list)
    assert meta["plan_intent"] in {"ir_receipts_summary","generic_safe_explore"}

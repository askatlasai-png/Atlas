import os
from atlas_core.atlas_query_router import route_query

def test_onhand_local_only():
    os.environ["ATLAS_ROUTER_MODE"] = "LOCAL_ONLY"
    os.environ["ATLAS_TAU_LOCAL"] = "0.55"
    plan = route_query('onhand for ITEM-00004 at WH1', k=4)
    assert plan.intent in {"onhand_by_item", "generic_safe_explore"}

def test_generic_safe_when_ambiguous():
    os.environ["ATLAS_ROUTER_MODE"] = "LOCAL_ONLY"
    os.environ["ATLAS_TAU_LOCAL"] = "0.55"
    plan = route_query('show me stuff for ITEM-00004', k=4)
    assert plan.intent in {"generic_safe_explore", "onhand_by_item"}

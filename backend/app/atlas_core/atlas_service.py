# atlas_service.py
from __future__ import annotations
import os
import time, uuid  # <-- add this
from typing import Any, Dict

try:
    from atlas_core.atlas_query_router import route_query  # required
    try:
        from atlas_core.atlas_query_router import clear_router_caches  # optional
    except Exception:
        clear_router_caches = None
    from atlas_core.atlas_plan_executor import PlanExecutor
    try:
        from atlas_core.atlas_plan_executor import clear_executor_caches  # optional
    except Exception:
        clear_executor_caches = None
except ImportError:  # pragma: no cover
    from .atlas_query_router import route_query  # required
    try:
        from .atlas_query_router import clear_router_caches  # optional
    except Exception:
        clear_router_caches = None
    from .atlas_plan_executor import PlanExecutor
    try:
        from .atlas_plan_executor import clear_executor_caches  # optional
    except Exception:
        clear_executor_caches = None


_EXECUTOR = PlanExecutor()

def _effective_mode(mode: str | None) -> str:
    return (mode or os.getenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY")).upper()

def run_query(q: str, k: int = 4, mode: str | None = None) -> Dict[str, Any]:
    import os, uuid, time

    req_id = f"{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}"
    eff_mode = _effective_mode(mode)

    # Optional: clear caches in debug for deterministic repros
    cache_cleared = False
    if os.getenv("ATLAS_DEBUG", "0") == "1":
        for fn in (clear_router_caches, clear_executor_caches):
            try:
                if callable(fn):
                    fn()
                    cache_cleared = True or cache_cleared
            except Exception:
                pass

    # ---- First pass (deterministic) ----
    plan = route_query(q, k=k, mode=eff_mode)
    out = _EXECUTOR.run(plan)

    meta = dict(out.get("meta", {}))
    meta.setdefault("plan_intent", getattr(plan, "intent", None))
    meta.setdefault("plan_rationale", getattr(plan, "rationale", None))
    meta.setdefault("mode", eff_mode)
    meta.setdefault("approximate", False)

    # include router debug if available
    if os.getenv("ATLAS_DEBUG") == "1":
        rd = getattr(plan, "router_debug", None)
        if rd:
            meta["router_debug"] = rd

    meta["request_id"] = req_id
    meta["debug"] = {
        "cache_cleared": cache_cleared,
        "atlas_debug": os.getenv("ATLAS_DEBUG", "0"),
    }

    rows = out.get("rows") or []
    out["rows"] = rows
    out["meta"] = meta

    # ---- Executor-level fallback on zero rows (guard with env) ----
    # Enable with: ATLAS_EXECUTOR_FALLBACK=1
    if (os.getenv("ATLAS_EXECUTOR_FALLBACK", "0") == "1") and (len(rows) == 0):
        try:
            fb_mode = "LOCAL_ONLY"
            fb_plan = route_query(q, k=k, mode=fb_mode)
            fb_out = _EXECUTOR.run(fb_plan)
            fb_rows = fb_out.get("rows") or []

            if fb_rows:
                fb_meta = dict(fb_out.get("meta", {}))
                fb_meta.setdefault("plan_intent", getattr(fb_plan, "intent", None))
                fb_meta.setdefault("plan_rationale", getattr(fb_plan, "rationale", None))
                fb_meta["mode"] = f"{eff_mode}+FALLBACK_LOCAL"
                fb_meta["approximate"] = True
                fb_meta["request_id"] = req_id
                fb_meta["debug"] = {
                    "cache_cleared": cache_cleared,
                    "atlas_debug": os.getenv("ATLAS_DEBUG", "0"),
                }
                fb_meta["warning"] = "deterministic_zero_rows→fallback_local"
                fb_meta["fallback"] = {
                    "trigger": "zero_rows",
                    "from_mode": eff_mode,
                    "to_mode": fb_mode,
                    "first_plan_intent": meta.get("plan_intent"),
                    "first_plan_rationale": meta.get("plan_rationale"),
                }
                fb_out["meta"] = fb_meta
                return fb_out
            else:
                meta["warning"] = "deterministic_zero_rows (fallback produced 0 rows)"
                out["meta"] = meta
                return out
        except Exception as e:
            meta["warning"] = f"deterministic_zero_rows (fallback_error={type(e).__name__})"
            out["meta"] = meta
            return out

    return out


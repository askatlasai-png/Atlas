# tests/test_transactional.py
import os
import pytest
from fastapi.testclient import TestClient

# Point to your csv_path.json (adjust if your path differs)
os.environ.setdefault(
    "ATLAS_CSV_CFG",
    r"C:\code\atlas-erp-chat-v1 - Copy\backend\app\csv_path.json"
)
os.environ.setdefault("ATLAS_DEBUG", "1")
os.environ.setdefault("ATLAS_ROUTER_MODE", "OPENAI_ONLY")

# Import the API app
from atlas_core.atlas_api import app  # noqa: E402

client = TestClient(app)


def _run(q: str):
    r = client.post("/query", json={"q": q})
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
    data = r.json()
    # Basic shape
    assert "rows" in data and "meta" in data, f"Bad response shape: {data}"
    return data


def _lineage_sources(meta):
    return [s.get("source") for s in (meta.get("lineage") or [])]


def _lineage_ops(meta):
    return [s.get("op") for s in (meta.get("lineage") or [])]


def _first_step(meta):
    steps = meta.get("lineage") or []
    return steps[0] if steps else None


def _last_step(meta):
    steps = meta.get("lineage") or []
    return steps[-1] if steps else None


def _has_col(rows, col):
    return bool(rows) and (col in rows[0])


def _find_step(meta, op):
    for s in meta.get("lineage") or []:
        if s.get("op") == op:
            return s
    return None


# -------------------------
# Happy-path TRANSACTIONAL
# -------------------------

def test_po_detail_specific():
    data = _run("Show details for PO-000173")
    meta, rows = data["meta"], data["rows"]
    assert _first_step(meta)["source"] == "PO"
    assert len(rows) >= 1


def test_buyer_leaderboard_count_then_sort():
    data = _run("Which buyer cut most purchase orders")
    meta, rows = data["meta"], data["rows"]

    # Must aggregate by buyer_user_id counting po_number
    agg = _find_step(meta, "aggregate")
    assert agg and agg.get("source") == "PO"
    assert "buyer_user_id" in (agg.get("params", {}).get("by") or [])
    metrics = agg.get("params", {}).get("metrics") or []
    assert metrics and metrics[0][0] == "po_number" and metrics[0][1].lower() == "count"

    # Sort should target the real output column (po_number), not 'count'
    sort = _find_step(meta, "sort")
    assert sort, "Missing sort step"
    by = sort.get("params", {}).get("by") or sort.get("params_in", {}).get("by") or []
    assert by and (by[0].lower() == "po_number")

    assert len(rows) > 0
    # The result table should have buyer_user_id and the count column (po_number)
    assert _has_col(rows, "buyer_user_id")
    assert _has_col(rows, "po_number")


def test_buyer_leaderboard_top10():
    data = _run("Which buyer cut most purchase orders show me top 10")
    meta, rows = data["meta"], data["rows"]
    assert _find_step(meta, "aggregate")
    tk = _find_step(meta, "topk")
    assert tk and (tk.get("k") == 10 or tk.get("params", {}).get("k") == 10)
    assert len(rows) <= 10


def test_so_group_by_carrier():
    data = _run("Group the sales orders by carrier name")
    meta, rows = data["meta"], data["rows"]
    assert _first_step(meta)["source"] == "SO"
    agg = _find_step(meta, "aggregate")
    assert agg, "Expected aggregate step for group_by"
    assert "carrier_name" in (agg.get("params", {}).get("by") or [])
    assert len(rows) > 0


# -------------
# LPN variants
# -------------

def test_lpn_items_detail():
    data = _run("List items in LPN-0000059")
    meta, rows = data["meta"], data["rows"]
    assert _first_step(meta)["source"] == "LPN"
    assert len(rows) > 0
    # item or uom columns are expected in LPN detail file; presence may vary by dataset
    assert _has_col(rows, "lpn_number"), "lpn_number should be present in LPN detail"


def test_lpn_serials_detail():
    data = _run("Show serial numbers in LPN-0000059")
    meta, rows = data["meta"], data["rows"]
    assert _first_step(meta)["source"] in ("LPN_SERIALS", "LPN_SERIAL"), "Should hit serials source"
    assert len(rows) >= 0  # can be 0 if that LPN has no serials
    # If there are rows, ensure serial_number column exists
    if rows:
        assert _has_col(rows, "serial_number"), "serial_number column missing"


def test_lpn_serial_counts():
    data = _run("Give serial counts by item for LPN-0000059")
    meta, rows = data["meta"], data["rows"]

    # Accept either pre-agg file or dynamic aggregate
    srcs = set(_lineage_sources(meta))
    ops  = set(_lineage_ops(meta))
    assert ("LPN_SERIALS_AGG" in srcs) or ("aggregate" in ops), "Expected agg over serials or pre-agg source"
    # Column check (only if rows exist)
    if rows:
        assert _has_col(rows, "lpn_number")
        # either pre-agg column 'serial_count' or aggregated 'lpn_number'/'item' with a count column
        serial_count_present = _has_col(rows, "serial_count")
        has_item = _has_col(rows, "item")
        assert serial_count_present or has_item, "Expected serial_count or item"


# --------------
# Edge/negative
# --------------

def test_bad_lpn_returns_zero_rows_no_exception():
    data = _run("Show serial numbers in LPN-DOESNOTEXIST")
    meta, rows = data["meta"], data["rows"]
    # Should target serials source and simply return 0 rows
    assert _first_step(meta)["source"] in ("LPN_SERIALS", "LPN_SERIAL")
    assert len(rows) == 0
    # No executor errors
    assert not (meta.get("errors") or []), f"errors present: {meta.get('errors')}"

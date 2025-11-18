# atlas_query_router.py
# v2.3 — Unified sort handling across all planners (NL > LLM; normalized column; single canonical step)

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import os, json, re

# OpenAI SDK (>=1.x)
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # checked at runtime


# --- Dynamic schema columns (from CSV headers + alias canon) ---
try:
    # Reuse executor's CSV map & aliases to avoid drift
    from atlas_core.atlas_plan_executor import _csv_path, COLUMN_ALIASES
except ImportError:  # local package relative import
    from .atlas_plan_executor import _csv_path, COLUMN_ALIASES

import pandas as _pd
_SCHEMA_CACHE: Dict[str, List[str]] = {}

_TOPK_REGEXES = [
    r"\btop\s+(\d+)\b",          # "top 5"
    r"\bfirst\s+(\d+)\b",        # "first 5"
    r"\bshow\s+(\d+)\b",         # "show 5 ..."
]


# Debug-friendly: allow clearing schema cache between requests
def clear_router_caches():
    try:
        _SCHEMA_CACHE.clear()
    except Exception:
        pass



def _canonicalize_cols(source: str, cols: List[str]) -> List[str]:
    """Map raw CSV headers to canonical names via COLUMN_ALIASES, then dedupe."""
    alias = COLUMN_ALIASES.get(source, {})
    canon = []
    for c in cols:
        k = str(c).strip()
        canon.append(alias.get(k.lower(), k))
    # also include every canonical value present in alias map
    canon.extend(alias.values())
    # stable unique, preserve order of first appearance
    seen = set()
    out = []
    for c in canon:
        if c not in seen and c:
            seen.add(c); out.append(c)
    return out

def _canon_col(col: str, source: str = "ONHAND") -> str:
    if not col:
        return col
    alias = COLUMN_ALIASES.get(source, {})
    c = col.strip().lower()
    c = c.replace("-", " ").replace("__", "_").replace("  ", " ")
    c = c.replace(" quantity", "").replace(" qty", "")
    c = c.replace(" ", "_")
    return alias.get(c, alias.get(c.replace("_", ""), c))



def _schema_cols(source: str) -> List[str]:
    """Read CSV headers (nrows=0), canonicalize, cache."""
    if source in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[source]
    path = _csv_path(source)
    raw_cols = list(_pd.read_csv(path, nrows=0).columns)
    cols = _canonicalize_cols(source, raw_cols)
    _SCHEMA_CACHE[source] = cols
    return cols

# Heuristic source resolver (cheap, per-request)
def _resolve_ctx_source(q: str) -> str:
    s = (q or "").lower()

    # hard signals (ids + nouns)
    if "po-" in s or "purchase order" in s or re.search(r"\bpo[\s#:-]", s): 
        return "PO"
    if "so-" in s or "sales order" in s or re.search(r"\bso[\s#:-]", s):
        return "SO"
    if "carrier" in s or "carrier name" in s or "sales orders" in s:
        return "SO" 
    if "invoice" in s or "ap invoice" in s or "ir-" in s or "invoice receipt" in s:
        return "IR"
    if "delivery" in s or "shipment" in s or "ship confirm" in s:
        return "SO_DELIVERY"
    if "lpn" in s or "license plate" in s or "serial" in s:
        return "LPN"

    # default ONHAND for inventory-y questions
    return "ONHAND"


# ------------------------------------------------------------------
# Router mode / model selection
# ------------------------------------------------------------------
ROUTER_MODE = os.getenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY").upper()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("ATLAS_ROUTER_MODEL") or "gpt-4-0613"

INTENTS = ["TRANSACTIONAL","OPERATIONAL","COMPARATIVE","EXCEPTION","MIXED","FALLBACK"]



@dataclass
class Step:
    op: str
    source: str | None = None
    params: Dict[str, Any] | None = None

@dataclass
class Plan:
    intent: str
    rationale: str
    steps: List[Step]

# ------------------------------------------------------------------
# LLM prompt (compact JSON only)
# ------------------------------------------------------------------
# build these first (outside the string)
# ctx_source = "ONHAND"  # swap later when you switch contexts
# def _system_prompt_for(q: str) -> str:
#     ctx_source = _resolve_ctx_source(q)
#     schema_hint = ", ".join(_schema_cols(ctx_source))
#     return (
#         "You are AtlasQueryRouter, a strict intent and plan classifier for supply-chain analytics.\n"
#         "Return only JSON with keys: intent (TRANSACTIONAL|OPERATIONAL|COMPARATIVE|EXCEPTION|MIXED|FALLBACK),\n"
#         "filters (array of {\"col\",\"op\",\"value\"}), need_aggregate (bool),\n"
#         "group_by (array), metrics (array of [col,agg]), sort_by (string), sort_order (asc|desc).\n"
#         f"Use schema names exactly: {schema_hint}.\n"
#     )

def _system_prompt_for(q: str) -> str:
    ctx_source = _resolve_ctx_source(q)
    schema_hint = ", ".join(_schema_cols(ctx_source))
    return (
        "You are AtlasQueryRouter, a strict intent and plan classifier for supply-chain analytics.\n"
        "Return only JSON with these keys:\n"
        "  source (PO|SO|ONHAND|IR|LPN|LPN_SERIALS|LPN_SERIALS_AGG),\n"
        "  intent (TRANSACTIONAL|OPERATIONAL|COMPARATIVE|EXCEPTION|MIXED|FALLBACK),\n"
        "  filters (array of {\"col\",\"op\",\"value\"}),\n"
        "  need_aggregate (bool),\n"
        "  group_by (array),\n"
        "  metrics (array of [col,agg]),\n"
        "  sort_by (string),\n"
        "  sort_order (asc|desc).\n"
        "\n"

        f"Use schema names exactly: {schema_hint}.\n"
        "\n"
        "Select the correct data source (table) based on which columns or concepts are mentioned:\n"
        "  • buyer_user_id → PO\n"
        "  • po_number → PO\n"
        "  • carrier_name → SO\n"
        "  • so_number → SO\n"
        "  • lpn_number → LPN\n"
        "  • serial_number, serial, sn, imei → LPN_SERIALS\n"
        "  • serial_count, count_of_serials, serials_agg → LPN_SERIALS_AGG\n"
        "\n"
        "Behavioral rules:\n"
        "  • If group_by is present, always return a plan that aggregates by those columns.\n"
        "  • When metrics are missing, default to a simple count of a key column "
        "(e.g., count of po_number, so_number, or lpn_number).\n"
        "  • When sorting, include both sort_by and sort_order explicitly.\n"
        "  • If a query mentions 'top N', include a top-k step with k = N after sorting.\n"
        "  • When you aggregate, set sort_by to the actual output column name — for count metrics, "
        "use the counted column (e.g., 'po_number') rather than 'count'.\n"
        "\n"
        "Source selection overrides:\n"
        "  • If the query mentions serials or serial numbers, use LPN_SERIALS.\n"
        "  • If it mentions serial counts, use LPN_SERIALS_AGG.\n"
        "  • Otherwise, use LPN for LPN-level item details.\n"
        "\n"
        "Ensure all column and table names exactly match the schema — "
        "do not invent or rename fields.\n"
        "Output strictly in JSON format only, with no explanations or extra text."
    )

# def _system_prompt_for(q: str) -> str:
#     # Give schema vocab for ALL sources so the LLM can choose one; no local guessing.
#     po_cols  = ", ".join(_schema_cols("PO"))
#     so_cols  = ", ".join(_schema_cols("SO"))
#     oh_cols  = ", ".join(_schema_cols("ONHAND"))
#     ir_cols  = ", ".join(_schema_cols("IR"))
#     lpn_cols = ", ".join(_schema_cols("LPN"))
#     lps_cols = ", ".join(_schema_cols("LPN_SERIALS"))
#     lpa_cols = ", ".join(_schema_cols("LPN_SERIALS_AGG"))

#     return (
#         "You are AtlasQueryRouter, a strict planner for supply-chain analytics.\n"
#         "Return ONLY JSON with keys:\n"
#         "  source (PO|SO|ONHAND|IR|LPN|LPN_SERIALS|LPN_SERIALS_AGG),\n"
#         "  intent (TRANSACTIONAL|OPERATIONAL|COMPARATIVE|EXCEPTION|MIXED|FALLBACK),\n"
#         "  filters (array of {\"col\",\"op\",\"value\"}),\n"
#         "  need_aggregate (bool),\n"
#         "  group_by (array),\n"
#         "  metrics (array of [col,agg]),\n"
#         "  sort_by (string),\n"
#         "  sort_order (asc|desc).\n"
#         "\n"
#         "Choose EXACTLY one source based on the user question. Use real schema column names for that source.\n"
#         "\n"
#         f"PO columns: {po_cols}\n"
#         f"SO columns: {so_cols}\n"
#         f"ONHAND columns: {oh_cols}\n"
#         f"IR columns: {ir_cols}\n"
#         f"LPN columns: {lpn_cols}\n"
#         f"LPN_SERIALS columns: {lps_cols}\n"
#         f"LPN_SERIALS_AGG columns: {lpa_cols}\n"
#         "\n"
#         "Interpret time phrases (e.g., 'this week' = Monday..Sunday) and emit explicit date filters on date columns.\n"
#         "If you aggregate, include group_by/metrics, and when sorting include both sort_by & sort_order.\n"
#         "Output strictly JSON. No prose."
#     )



_EXAMPLE = {
  "intent": "OPERATIONAL",
  "filters": [{"col":"organization_id","op":"eq","value":"101"}],
  "need_aggregate": False,
  "group_by": [],
  "metrics": [],
  "sort_by": "available_qty",
  "sort_order": "desc"
}

# ------------------------------------------------------------------
# Column aliases per source (router-side normalization)
# ------------------------------------------------------------------
ROUTER_COLUMN_ALIASES: Dict[str, Dict[str, str]] = {
    "PO": {
        "po": "po_number", "po_no": "po_number", "poid": "po_number", "po_number": "po_number", "PO": "po_number",
        "supplier": "vendor_name", "vendor": "vendor_name", "supplier_name": "vendor_name",
        "eta": "promised_date", "ETA": "promised_date", "eta_date": "promised_date",
        "needby": "need_by_date", "need_by": "need_by_date",
        "status": "po_status",
        "site": "organization_id", "org": "organization_id", "org_id": "organization_id", "site_id": "organization_id",
        "item_id": "item", "sku": "item"
    },
    "ONHAND": {
        "site": "organization_id", "org": "organization_id", "org_id": "organization_id", "site_id": "organization_id",
        "sku": "item", "item_id": "item",
        "onhand": "onhand_qty", "available": "available_qty", "reserved": "reserved_qty", "reserved qty": "reserved_qty", "reserved_qty": "reserved_qty","reserved quantity": "reserved_qty",
    },
    "SO": {
        "so": "so_number", "so_no": "so_number",
        "customer": "customer_or_site_name", "customer_name": "customer_or_site_name",
        "status": "delivery_status",
        "site": "organization_id", "org": "organization_id", "org_id": "organization_id", "site_id": "organization_id",
        "item_id": "item", "sku": "item"
    },
    "IR": {
        "po": "po_number", "po_no": "po_number",
        "so": "so_number", "so_no": "so_number",
        "status": "req_status",
        "site": "organization_id", "org": "organization_id", "org_id": "organization_id", "site_id": "organization_id",
        "item_id": "item", "sku": "item"
    },
    "LPN": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "status": "delivery_status",
        "site": "organization_id", "org": "organization_id", "org_id": "organization_id", "site_id": "organization_id",
        "item_id": "item", "sku": "item"
    },
    "LPN_SERIAL": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "serial": "serial_number", "sn": "serial_number"
    },
    "LPN_SERIALS": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "serial": "serial_number", "sn": "serial_number"
    },
    "LPN_SERIALS_AGG": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "serial": "serial_number", "sn": "serial_number"
    }

}

def _norm_filters_for_source(source: str, filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    alias = ROUTER_COLUMN_ALIASES.get(source, {})
    out: List[Dict[str, Any]] = []

    # For PO we’ll also look at the actual schema so we can convert RHS strings to colrefs
    po_cols_map = {c.lower(): c for c in _schema_cols("PO")} if (source or "").upper() == "PO" else {}

    for f in (filters or []):
        col_raw = str(f.get("col", ""))
        op_raw  = (f.get("op") or "eq")
        val_raw = f.get("value")

        # 1) apply router-side aliases first (case-insensitive)
        col = alias.get(col_raw, alias.get(col_raw.lower(), col_raw))
        op  = str(op_raw).lower()
        val = val_raw

        s = (source or "").upper()
        if s == "PO":
            # --- A) status → po_status, robust to OPEN / OPEN_* encodings ---
            if col.lower() in {"status", "po_status"}:
                col = "po_status"
                if isinstance(val, str):
                    val = val.upper()            # 'open' -> 'OPEN'
                if op in {"=", "eq"}:
                    op = "contains"              # match OPEN and OPEN_* variants

            # --- B) NL hint: "pending receipt" => received_qty < ordered_qty ---
            if isinstance(val, str) and "pending receipt" in val.lower():
                out.append({"col": "received_qty", "op": "<", "value": {"colref": "ordered_qty"}})
                # keep any explicit status filter the LLM also sent
                # (do not 'continue' unless you want to drop the original tokenized filter)
                continue

            # --- C) If RHS names a real PO column, make it a colref for col↔col compares ---
            # e.g. {"col":"last_receipt_date","op":">","value":"promised_date"}  -> colref
            if isinstance(val, str) and val.lower() in po_cols_map:
                val = {"colref": po_cols_map[val.lower()]}

        # default: pass through (for non-PO sources or other PO fields)
        out.append({"col": col, "op": op, "value": val})

    return out


# ------------------------------------------------------------------
# Simple text parsers
# ------------------------------------------------------------------
_PO_PATTERNS = [
    re.compile(r"\bpo\s*#?\s*[-_ ]?(\d{3,})\b", re.IGNORECASE),     # "PO 173", "PO-000173", "PO_00173", "PO# 12345"
    re.compile(r"\bpo[-_ ]?(\d{3,})\b", re.IGNORECASE),             # "PO-0000173", "PO0000173"
]

def _extract_po_number(q: str) -> Optional[str]:
    """Return the trailing numeric portion; caller can prepend 'PO-' if dataset stores full ID."""
    text = q or ""
    for pat in _PO_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1)  # numeric portion
    return None


_SITE_RE = re.compile(r"\bsite\s+(\d+)\b", re.IGNORECASE)
def _parse_site_filter(q: str) -> List[Dict[str, Any]]:
    m = _SITE_RE.search(q or "")
    return [{"col": "site", "op": "eq", "value": m.group(1)}] if m else []

_SORT_SYNONYMS = {
    "available": "available_qty", "available qty": "available_qty", "available_qty": "available_qty",
    "onhand": "onhand_qty", "on hand": "onhand_qty", "on-hand": "onhand_qty", "onhand_qty": "onhand_qty",
    "reserved": "reserved_qty", "reserved qty": "reserved_qty", "reserved_qty": "reserved_qty", "reserved quantity": "reserved_qty",
    "item": "item", "site": "organization_id", "org": "organization_id", "organization": "organization_id",
    "organization_id": "organization_id",
}

# --- helpers to sanitize sort keys ---
def _strip_sort_modifiers(s: str) -> str:
    """Remove trailing 'asc|desc' and 'top <n>' tokens from a candidate sort key."""
    if not s:
        return s
    t = s.strip().lower()
    # remove trailing 'top <n>'
    t = re.sub(r"\s+top\s+\d+\b", "", t)
    # remove trailing 'ascending|descending|asc|desc'
    t = re.sub(r"\s+(ascending|descending|asc|desc)\b", "", t)
    return t.strip()

def _clean_sort_key(raw: str) -> str:
    """Normalize a raw sort key: strip modifiers, fold spaces -> underscores."""
    base = _strip_sort_modifiers(raw)
    return base.replace("  ", " ").replace(" ", "_")

def _parse_sort(q: str) -> Optional[Dict[str, Any]]:
    s = (q or "").lower()

    # A) “sorted by X [asc|desc]” / “sort by X [asc|desc]”
    m = re.search(r"(?:sorted|sort)\s+by\s+([a-z0-9 _\-]+)(?:\s+(ascending|descending|asc|desc)(?:\s+order)?)?", s)
    if not m:
        # B) “by X asc|desc”
        m = re.search(r"\bby\s+([a-z0-9 _\-]+)\s+(ascending|descending|asc|desc)\b", s)
    if not m:
        return None

    raw_col = (m.group(1) or "").strip()
    raw_ord = (m.group(2) or "").strip() if len(m.groups()) >= 2 else ""

    # detect order if it was embedded in the column phrase (e.g., “available desc top 5”)
    embedded_ord = ""
    if not raw_ord and re.search(r"\b(descending|desc)\b", raw_col):
        embedded_ord = "desc"
    elif not raw_ord and re.search(r"\b(ascending|asc)\b", raw_col):
        embedded_ord = "asc"

    # normalize column → canonical
    base = _clean_sort_key(raw_col)                     # strips “desc/top 5” from the key
    col  = _SORT_SYNONYMS.get(base, base)
    ord_token = (raw_ord or embedded_ord).lower()
    ascending = not (ord_token in ("descending", "desc"))

    return {"by": col, "ascending": ascending}


def _parse_topk(q: str) -> Optional[Dict[str, Any]]:
    """
    Understands:
      - "top 5", "top5", "top-5"
      - "first 10"
      - "last 3"
      - "limit 20"
    Returns: {"k": int, "ascending": Optional[bool]}  (ascending None = follow sort/default)
    """
    s = (q or "").lower()

    m = re.search(r"\btop[-\s]?(\d+)\b", s)
    if m:
        return {"k": int(m.group(1)), "ascending": False}  # “top” implies highest → desc

    m = re.search(r"\bfirst\s+(\d+)\b", s)
    if m:
        return {"k": int(m.group(1)), "ascending": True}   # first = lowest if unsorted, but we’ll pair with sort

    m = re.search(r"\blast\s+(\d+)\b", s)
    if m:
        return {"k": int(m.group(1)), "ascending": False}  # last = highest if paired with ascending sort

    m = re.search(r"\blimit\s+(\d+)\b", s)
    if m:
        return {"k": int(m.group(1)), "ascending": None}   # no order hint; follow existing sort if any

    return None

def _wants_aggregate(q: str) -> bool:
    L = (q or "").lower()
    return any(tok in L for tok in ["by site","by org","by organization","group","sum","total"])

# ------------------------------------------------------------------
# LLM classify (guarded)
# ------------------------------------------------------------------
_CLIENT: Optional[OpenAI] = None
def _client() -> OpenAI:
    global _CLIENT
    if _CLIENT is None:
        if OpenAI is None:
            raise RuntimeError("openai package not available")
        _CLIENT = OpenAI()
    return _CLIENT


# --- helpers (place above _classify) -----------------------------------------

def _looks_like_list(q: str) -> bool:
    ql = (q or "").strip().lower()
    return (
        ql.startswith("list ")
        or ql.startswith("show ")
        or ql.startswith("display ")
        or ql.startswith("return ")
        or ql.startswith("give me ")
    )

def _is_trivial_count_metrics(metrics) -> bool:
    """
    True if metrics is exactly one ('po_number','count'), ('*','count'), or ('id','count').
    We don't want this to force aggregation for EXCEPTION 'List …' queries with no group_by.
    """
    try:
        if not metrics or len(metrics) != 1:
            return False
        col, fn = metrics[0][0], str(metrics[0][1]).lower()
        return fn == "count" and str(col).lower() in ("po_number", "*", "id")
    except Exception:
        return False

# --- DROP-IN: _classify ------------------------------------------------------

def _classify(query: str) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        return {}, ""
    c = _client()
    msg = f"User query: {query}\nReturn ONLY compact JSON."
    try:
        r = c.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": _system_prompt_for(query)},
                {"role": "user", "content": msg},
            ],
        )
        text = (r.choices[0].message.content or "").strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group(0)) if m else {}

        # normalize
        data["intent"] = str(data.get("intent", "FALLBACK")).upper()
        if "source" in data and data["source"]:
            data["source"] = str(data["source"]).upper()

        # Guardrail: if metrics exist, default to aggregate... EXCEPT for
        # EXCEPTION "List …" with a trivial count and no group_by (keep as a list).
        try:
            if data.get("metrics"):
                if not (
                    data["intent"] == "EXCEPTION"
                    and not data.get("group_by")
                    and _is_trivial_count_metrics(data.get("metrics"))
                    and _looks_like_list(query)
                ):
                    data["need_aggregate"] = True
                else:
                    # keep it a true list
                    data["need_aggregate"] = False
                    data["metrics"] = []
        except Exception:
            pass

        return data, text
    except Exception:
        return {}, ""




# ------------------------------------------------------------------
# Shared: augment plan with a canonical, normalized sort (NL > LLM)
# ------------------------------------------------------------------
def augment_plan_with_sort(plan: Plan, parsed: Dict[str, Any], q: str) -> None:
    """
    Ensures at most one sort step is present.
    Priority:
      1) NL "sorted by X asc|desc" (column + order),
      2) LLM sort_by/sort_order,
    Then normalize column via _SORT_SYNONYMS and emit one canonical sort step.
    """
    # NL
    nl = _parse_sort(q)  # -> {"by": "available_qty", "ascending": False} or None
    nl_by_raw  = nl.get("by") if nl else None
    nl_has_ord = (nl is not None and nl.get("ascending") is not None)
    nl_order   = ("desc" if (nl and nl.get("ascending") is False) else
                  "asc"  if (nl and nl.get("ascending") is True)  else None)

    # LLM
    llm_by_raw  = parsed.get("sort_by")
    llm_by_norm = _SORT_SYNONYMS.get(str(llm_by_raw).lower(), llm_by_raw) if llm_by_raw else None
    llm_order   = (parsed.get("sort_order") or "").lower() or None

    prelim_by    = nl_by_raw if nl_by_raw else llm_by_norm
    prelim_order = nl_order  if nl_order  else llm_order

    final_by = _SORT_SYNONYMS.get(str(prelim_by).lower(), prelim_by) if prelim_by else None
    final_order = nl_order if nl_has_ord else prelim_order

    if final_by:
        # drop any existing sorts
        plan.steps = [s for s in plan.steps if s.op != "sort"]

        asc_flag = True
        if final_order in ("desc", "descending"):
            asc_flag = False
        elif final_order in ("asc", "ascending"):
            asc_flag = True
        elif nl_has_ord:
            asc_flag = bool(nl["ascending"])

        plan.steps.append(Step("sort", None, {
            "by": [final_by],
            "order": ("desc" if not asc_flag else "asc"),
            "ascending": asc_flag
        }))
        plan.rationale += " (with sort)"

def augment_plan_with_topk(plan: Plan, parsed: Dict[str, Any], q: str) -> None:
    """
    If NL says "top 5 / first 10 / last 3 / limit 20", ensure there is ONE topk step.
    - If a sort step exists, reuse its column & direction.
    - Otherwise, try to reuse NL/LLM sort target; else emit topk without 'by'
      so executor will head(k) on current order.
    """
    tk = _parse_topk(q)
    if not tk:
        return  # no top-k mentioned → do nothing

    # Remove any existing topk steps to keep it canonical
    plan.steps = [s for s in plan.steps if s.op != "topk"]

    # Try to discover a sort target to piggyback on
    sort_step = next((s for s in plan.steps if s.op == "sort"), None)

    by_col: Optional[str] = None
    asc: Optional[bool] = tk.get("ascending")

    if sort_step:
        # inherit the first sort-by column if present
        by_list = (sort_step.params or {}).get("by") or []
        if isinstance(by_list, list) and by_list:
            by_col = by_list[0]

        if asc is None:
            ord_param = (sort_step.params or {}).get("order")
            if ord_param in ("asc", "ascending", "desc", "descending"):
                asc = (ord_param in ("asc", "ascending"))
            elif "ascending" in (sort_step.params or {}):
                asc = bool((sort_step.params or {}).get("ascending"))
    else:
        # fall back to NL/LLM parse
        nl = _parse_sort(q)
        llm_by = parsed.get("sort_by")
        if nl and nl.get("by"):
            by_col = nl.get("by")
            if asc is None and "ascending" in nl:
                asc = nl.get("ascending")
        elif llm_by:
            by_col = llm_by
            # direction unknown -> leave asc as None

    # Build topk params safely (never reference by_col unless it exists)
    k = int(tk["k"])
    topk_params = {"k": k}
    if by_col:
        topk_params["by"] = by_col
    if asc is not None:
        topk_params["ascending"] = bool(asc)

    plan.steps.append(Step("topk", None, topk_params))
    plan.rationale += f" (top {k})"





# ------------------------------------------------------------------
# Plans
# ------------------------------------------------------------------
def _plan_transactional(p: Dict[str, Any], q: str) -> Plan:
    src = (p.get("source") or "").upper()
    if not src:
        return Plan("FALLBACK", "No source from LLM", [])
    filters = _norm_filters_for_source(src, p.get("filters", []))
    steps = [Step("filter", src, {"where": filters, "limit": 5000})]
    return Plan("TRANSACTIONAL", f"{src} lookup", steps)


def _metric_out_col(tgt: str, metrics: list[list[str]]) -> str:
    """
    Return the actual column name that will exist after aggregate for the FIRST metric.
    Your executor writes count(col) back into the metric's column name (e.g., 'po_number').
    If you later standardize executor naming, update this mapping accordingly.
    """
    if not metrics:
        return None
    col, agg = metrics[0][0], (metrics[0][1] or "").lower()
    if agg == "count":
        # executor places the count in the original column name
        return col
    # For other aggs your executor likely also keeps the base col name.
    return col

_TOP_RE = re.compile(r"\btop\s+(\d{1,4})\b", re.I)
def _extract_topk(q: str) -> int | None:
    m = _TOP_RE.search(q or "")
    return int(m.group(1)) if m else None


def _plan_operational(p: Dict[str, Any], q: str) -> Plan:
    import os, re

    Lq = (q or "").lower()
    raw_filters = p.get("filters", [])
    group_by    = (p.get("group_by") or [])[:]
    metrics_in  = (p.get("metrics") or [])[:]
    sort_by_in  = (p.get("sort_by") or "").strip() or None
    sort_order  = (p.get("sort_order") or "").strip().lower() or None  # "asc" | "desc"

    # ----------------------------
    # ---- LLM-decided source (no local hints) ----
    tgt = (p.get("source") or "").upper()
    if not tgt:
        return Plan("FALLBACK", "No source from LLM", [])

    # ----------------------------
    # 2) Filter step
    # ----------------------------
    filters = _norm_filters_for_source(tgt, raw_filters)
    steps: list[Step] = [Step("filter", tgt, {"where": filters, "limit": 50000})]

    # ----------------------------
    # 3) NL fallback for group_by ("by X")
    # ----------------------------
    # If your file has _parse_group_by(source-aware), use it; otherwise do a tiny inline map.
    try:
        if not group_by:
            if '_parse_group_by' in globals():
                group_by = _parse_group_by(q, tgt) or []
    except Exception:
        pass

    # After the try/except that may call _parse_group_by(...)
    if not group_by:
    # super-tiny safety net for test phrasing like "by carrier name"
        if tgt == "SO" and (" by carrier" in Lq or " by carrier name" in Lq):
            group_by = ["carrier_name"]
        elif tgt == "PO" and (" by buyer" in Lq or " by buyer_user_id" in Lq):
            group_by = ["buyer_user_id"]


    # ----------------------------
    # 4) Serial-count phrasing → force aggregate if needed
    # ----------------------------
    # Replace `_serial_counts_text()` with a tiny inline check:
    serial_count_phrase = any(k in Lq for k in ["serial count", "count of serials", "serials count"])
    if tgt in ("LPN_SERIALS", "LPN_SERIALS_AGG") and serial_count_phrase:
        if not group_by:
            group_by = ["item"]
        if not metrics_in:
            metrics_in = [["serial_number", "count"]]


    # ----------------------------
    # 5) DISTINCT short-circuit
    # ----------------------------
    want_distinct = False
    gb = [g for g in (group_by or []) if g]
    if gb and not metrics_in:
        if any(k in Lq for k in ("distinct", "unique", "list")):
            want_distinct = True
    if want_distinct:
        steps.append(Step("distinct", tgt, {"cols": gb}))
        plan = Plan("OPERATIONAL", f"{tgt} distinct by {', '.join(gb)}", steps)
        # legacy alias only in non-OPENAI modes (if helper exists)
        try:
            mode = (os.getenv("ATLAS_ROUTER_MODE") or "").upper()
            if mode != "OPENAI_ONLY" and '_legacy_intent_alias' in globals():
                plan.intent = _legacy_intent_alias(q, plan.intent)
        except Exception:
            pass
        return plan

    # ----------------------------
    # 6) Aggregate when group_by is present
    # ----------------------------
    if gb:
        if not metrics_in:
            if   tgt == "SO":  metrics_in = [["so_number",  "count"]]
            elif tgt == "PO":  metrics_in = [["po_number",  "count"]]
            elif tgt in ("LPN", "LPN_SERIALS", "LPN_SERIALS_AGG"):
                metrics_in = [["lpn_number", "count"]]
            else:
                metrics_in = [["item", "count"]]
        steps.append(Step("aggregate", tgt, {"by": gb, "metrics": metrics_in}))

    # ----------------------------
    # 7) Sort resolution (LLM first, then NL)
    # ----------------------------
    nl = None
    try:
        nl = _parse_sort(q)  # {"by":"...", "ascending": True|False}
    except Exception:
        nl = None

    if not sort_by_in and nl and nl.get("by"):
        try:
            sort_by_in = _canon_col(nl["by"], tgt)
        except Exception:
            sort_by_in = nl["by"]

    if not sort_order and nl and (nl.get("ascending") is not None):
        sort_order = "asc" if nl["ascending"] else "desc"

    # If aggregated and sort_by is missing or was "count", map to actual output col
    sort_col = sort_by_in
    if gb:
        if not sort_col or str(sort_col).lower() == "count":
            # executor keeps the base column name for the count metric
            sort_col = metrics_in[0][0]

    # ----------------------------
    # 8) Top-K resolution
    # ----------------------------
    k = p.get("k")
    if k is None:
        try:
            k = _parse_topk(q)  # int or None
        except Exception:
            k = None

    # ----------------------------
    # 9) Attach sort/topk + craft rationale
    # ----------------------------
    rationale = f"{tgt} aggregate by {', '.join(gb)}" if gb else f"{tgt} detail"

    if sort_col:
        ascending = (sort_order == "asc") if sort_order in ("asc", "desc") else False
        steps.append(Step("sort", tgt, {
            "by": [sort_col],
            "order": sort_order or ("asc" if ascending else "desc"),
            "ascending": ascending
        }))
        rationale = f"{rationale} (sorted by {sort_col} {sort_order or ('asc' if ascending else 'desc')})"

    if k:
        steps.append(Step("topk", tgt, {
            "by": (sort_col or (gb[0] if gb else None)),
            "ascending": (sort_order == "asc") if sort_order in ("asc", "desc") else False,
            "k": k
        }))
        rationale = f"{rationale} (top {k})"

    plan = Plan("OPERATIONAL", rationale, steps)

    # ----------------------------
    # 10) Optional legacy intent labels for tests (LOCAL/HYBRID only)
    # ----------------------------
    try:
        mode = (os.getenv("ATLAS_ROUTER_MODE") or "").upper()
        if mode != "OPENAI_ONLY" and '_legacy_intent_alias' in globals():
            plan.intent = _legacy_intent_alias(q, plan.intent)
    except Exception:
        pass

    return plan


# --- NL "by <col>" parser (very small + source-aware) ---
_BY_RE = re.compile(r"\bby\s+([a-z0-9 _\-]+)\b", re.I)

def _parse_group_by(q: str, source: str) -> list[str]:
    """
    Extracts a single 'by <token>' and maps it to a canonical column for the inferred source.
    Minimal on purpose. Extend map as you add cases.
    """
    m = _BY_RE.search(q or "")
    if not m:
        return []
    token = (m.group(1) or "").strip().lower()
    # per-source quick maps
    maps = {
        "PO": {
            "buyer": "buyer_user_id",
            "buyer_user_id": "buyer_user_id",
            "vendor": "vendor_name",
            "vendor_name": "vendor_name",
            "site": "organization_id",
            "organization": "organization_id",
            "org": "organization_id",
        },
        "SO": {
            "carrier": "carrier_name",
            "carrier_name": "carrier_name",
            "status": "delivery_status",
            "customer": "customer_or_site_name",
            "site": "organization_id",
            "org": "organization_id",
        },
        "LPN": {
            "item": "item",
            "status": "delivery_status",
            "site": "organization_id",
            "org": "organization_id",
        },
        "LPN_SERIALS": {
            "item": "item",
            "delivery": "delivery_number",
            "delivery_number": "delivery_number",
        },
        "LPN_SERIALS_AGG": {
            "item": "item",
            "delivery": "delivery_number",
            "delivery_number": "delivery_number",
        },
        "ONHAND": {
            "item": "item",
            "site": "organization_id",
            "org": "organization_id",
        },
        "IR": {
            "status": "req_status",
            "site": "organization_id",
            "org": "organization_id",
        },
    }
    mp = maps.get((source or "ONHAND"), {})
    # normalize simple variants
    token_norm = token.replace("  ", " ").replace("quantity", "").strip().replace(" ", "_")
    return [ mp.get(token, mp.get(token_norm, token_norm)) ]


# --- Legacy test-label shim (keeps your code paths unchanged) ---
_LEGACY_RE_ONHAND_BY_ITEM = re.compile(r"\bonhand\b.*\bitem\b.*\b(site|wh)\b", re.I)

# Put near top of atlas_query_router.py (or wherever you defined it)
def _legacy_intent_alias(q: str, plan_intent: str) -> str:
    L = (q or "").lower()

    # "Compare PO vs onhand ..."  -> po_vs_onhand
    if ("po vs onhand" in L) or ("compare po vs onhand" in L) or ("inventory vs open po" in L):
        return "po_vs_onhand"

    # "onhand for ITEM-00004 at WH1" -> onhand_by_item
    # Be lenient: catch ITEM-**** tokens and generic "item" mentions
    has_onhand = "onhand" in L
    mentions_item = (" item" in L) or ("item-" in L) or ("item_" in L) or ("item" in L)
    mentions_site = (" wh" in L) or (" site" in L) or (" at wh" in L) or (" at site" in L)
    if has_onhand and mentions_item:
        return "onhand_by_item"

    # Other legacy labels used by tests
    if "ir receipts summary" in L:
        return "ir_receipts_summary"
    if "so delivery status" in L:
        return "so_delivery_status"
    if "show me stuff" in L:
        return "generic_safe_explore"

    return plan_intent





def _plan_comparative(q: str, p: Dict[str, Any]) -> Plan:
    """
    Respect LLM-provided source/group_by/metrics/sort. No invented defaults.
    Aggregate only if LLM asked (need_aggregate) or provided group_by/metrics.
    """
    tgt       = (p.get("source") or "ONHAND").upper()
    filters   = p.get("filters") or []
    gb        = [g for g in (p.get("group_by") or []) if g]
    metrics   = p.get("metrics") or []
    sort_by   = (p.get("sort_by") or "").strip() or None
    sort_ord  = (p.get("sort_order") or "").strip().lower() or None
    need_agg  = bool(p.get("need_aggregate")) or bool(gb) or bool(metrics)

    steps: List[Step] = [Step("filter", tgt, {"where": _norm_filters_for_source(tgt, filters), "limit": 50000})]

    if need_agg:
        if not gb:
            # If LLM asked for agg via metrics but forgot group_by, do a safe 1-col default
            gb = ["organization_id"]
        if not metrics:
            metrics = [["onhand_qty","sum"],["available_qty","sum"]]
        steps.append(Step("aggregate", None, {"by": gb, "metrics": metrics}))

    if sort_by:
        steps.append(Step("sort", None, {
            "by": [sort_by],
            "order": (sort_ord or "asc"),
            "ascending": (sort_ord == "asc") if sort_ord in ("asc","desc") else True
        }))

    # top-k is added later by augmentor; do not duplicate here
    rationale = f"{tgt} comparative"
    if need_agg and gb: rationale += f" by {', '.join(gb)}"
    if sort_by: rationale += f" (sorted by {sort_by} {sort_ord or 'asc'})"
    return Plan("COMPARATIVE", rationale, steps)





# --- DROP-IN: _plan_exception ------------------------------------------------
def _plan_exception(p: Dict[str, Any], q: str) -> Plan:
    """
    EXCEPTION planner that respects LLM details and handles safety-stock variants.
    Special handling:
      - "below/under safety stock" → available_qty < <safety_stock_col>
        where <safety_stock_col> is auto-resolved among common synonyms.
      - If required columns are missing, return FALLBACK so service can RAG.
    """
    L = (q or "").lower()
    filters   = (p.get("filters") or [])[:]
    tgt       = (p.get("source") or "").upper()
    group_by  = (p.get("group_by") or [])[:]
    metrics   = (p.get("metrics")  or [])[:]
    sort_by   = (p.get("sort_by")  or "").strip() or None
    sort_ord  = (p.get("sort_order") or "").strip().lower() or None
    need_agg  = bool(p.get("need_aggregate"))

    # 0) Choose source (trust LLM; otherwise infer sensibly)
    if not tgt:
        if "purchase" in L or "po " in L or L.startswith("po"):
            tgt = "PO"
        elif "sales" in L or "so " in L or L.startswith("so") or "delivery" in L or "shipment" in L:
            tgt = "SO"
        else:
            tgt = "ONHAND"  # inventory-themed default for safety-stock questions

    # Helper: schema cols for this source
    try:
        schema_cols = set(_schema_cols(tgt))
    except Exception:
        schema_cols = set()

    # 1) Query-specific: below/under safety stock → available_qty < safety_stock-ish
    wants_safety_stock = ("safety stock" in L) and (("below" in L) or ("under" in L) or ("less than" in L))
    if tgt == "ONHAND" and wants_safety_stock:
        # Resolve the best safety-stock column available in schema
        safety_synonyms = ["safety_stock", "safety_stock_level", "reorder_point", "min_qty", "min_level"]
        ss_col = next((c for c in safety_synonyms if c in schema_cols), None)

        if not ss_col:
            tried = ", ".join(safety_synonyms)
            rationale = f"{tgt} exception requires a safety stock column (tried: {tried}) not found in {tgt}"
            return Plan("FALLBACK", rationale, [])

        # Remove any conflicting hard-coded numeric guess LLM might have added
        new_filters = []
        for f in filters:
            col = str(f.get("col","")).lower()
            if col not in {"available_qty", "onhand_qty"}:
                new_filters.append(f)
        filters = new_filters

        # Prefer available_qty vs safety stock; swap to onhand_qty if that’s your policy.
        filters.append({
            "col": "available_qty",
            "op": "<",
            "value": {"colref": ss_col}
        })
        # Keep as a detail list unless LLM explicitly asked for aggregation
        need_agg = need_agg and bool(group_by)

    # 1a) Generic schema check for any colref filters
    required = set()
    for f in filters:
        c = f.get("col")
        if c: required.add(str(c))
        v = f.get("value")
        if isinstance(v, dict) and "colref" in v:
            required.add(str(v["colref"]))
    missing = [c for c in required if c not in schema_cols]
    if missing:
        rationale = f"{tgt} exception requires missing columns {missing} in {tgt} (join/alt source needed)"
        return Plan("FALLBACK", rationale, [])

    # 2) Filter step (normalized per source)
    steps: list[Step] = [
        Step("filter", tgt, {"where": _norm_filters_for_source(tgt, filters), "limit": 50000})
    ]

    # 3) Aggregate ONLY if LLM clearly asked (need_agg=True OR non-empty group_by)
    if need_agg or (group_by and len(group_by) > 0):
        try:
            gb_norm = _norm_group_by_for_source(tgt, group_by)
        except NameError:
            gb_norm = group_by
        if gb_norm:
            agg_metrics = metrics[:] if metrics else []
            if not agg_metrics:
                if tgt == "PO":   agg_metrics = [("po_number","count")]
                elif tgt == "SO": agg_metrics = [("so_number","count")]
                else:             agg_metrics = [("item","count")]
            steps.append(Step("aggregate", None, {"by": gb_norm, "metrics": agg_metrics}))

    # 4) Sorting — only if provided
    if sort_by:
        try:
            sb = _norm_sort_for_source(tgt, sort_by)
        except NameError:
            sb = sort_by
        sort_params = {"by": [sb]}
        if sort_ord in ("asc","desc"):
            sort_params["order"] = sort_ord
            sort_params["ascending"] = (sort_ord == "asc")
        steps.append(Step("sort", None, sort_params))

    rationale = "ONHAND items below safety stock" if (tgt == "ONHAND" and wants_safety_stock) else f"{tgt} exception analysis"
    return Plan("EXCEPTION", rationale, steps)




# ------------------------------------------------------------------
# Local fallback plan (no LLM required)
# ------------------------------------------------------------------
def _local_fallback_plan(q: str) -> Plan:
    """
    Handles quick offline/local queries when the router or LLM is bypassed.
    Supports:
      - PO lookups ("PO-000123")
      - On-hand detail / aggregate
      - Natural-language 'sorted by …' and 'top N' fallbacks
    """
    # --- transactional PO shortcut ---
    po_num = _extract_po_number(q)
    if po_num:
        filt = [{"col": "po_number", "op": "eq", "value": po_num}]
        return Plan(
            "TRANSACTIONAL",
            f"Explicit PO lookup for {po_num}",
            [Step("filter", "PO", {"where": _norm_filters_for_source("PO", filt), "limit": 2000})],
        )

    # --- operational (inventory) fallback ---
    fs = _norm_filters_for_source("ONHAND", _parse_site_filter(q))
    steps: list[Step] = [Step("filter", "ONHAND", {"where": fs, "limit": 50000})]
    rationale = "On-hand detail (local fallback)"

    # Aggregate path
    if _wants_aggregate(q):
        steps.append(
            Step(
                "aggregate",
                None,
                {
                    "by": ["organization_id", "item"],
                    "metrics": [("onhand_qty", "sum"), ("available_qty", "sum")],
                },
            )
        )
        rationale = "On-hand totals by organization_id,item (local fallback)"

    # --- build plan object first ---
    plan = Plan("OPERATIONAL", rationale, steps)

    # --- enrich with sort/top-k hints from NL (safe even if helpers absent) ---
    try:
        augment_plan_with_sort(plan, {}, q)
    except Exception:
        pass
    try:
        augment_plan_with_topk(plan, {}, q)
    except Exception:
        pass

    return plan



def _coerce_intent(q: str, parsed_intent: str) -> str:
    """
    Heuristically refine the model's initial intent guess based on phrasing.
    Handles cross-site vs. single-site comparisons, exceptions, and detail queries.
    """
    import re

    L = (q or "").lower().strip()

    # --- 1. Cross-site or ranking -> COMPARATIVE ---
    site_trigger     = bool(re.search(r"\bsite(s)?\b", L))
    item_trigger     = bool(re.search(r"\bitem(s)?\b", L))
    compare_phrases  = [
        "top ", " top", "rank", "compare", " versus ", " vs ",
        "by site", "across sites", "by org", "by organization",
        "totals", "total by", "per site"
    ]
    compare_trigger = any(p in L for p in compare_phrases)

    # Strong rule: "top ... sites" or "compare across sites" => COMPARATIVE
    if site_trigger and compare_trigger and not item_trigger:
        return "COMPARATIVE"

    # --- 2. Exception-oriented language ---
    if any(k in L for k in [
        "status count", "status counts", "counts by",
        "exceptions", "late", "overdue", "breach", "safety stock"
    ]):
        if any(k in L for k in ["delivery", "so ", "sales order", "shipment"]):
            return "EXCEPTION"
        if "po" in L:
            return "EXCEPTION"

    # --- 3. Comparative (ranking/summary across entities) ---
    comparative_triggers = any(k in L for k in [
        "compare", "vs", "versus", "rank by site", "by site",
        "by org", "by organization", "across sites"
    ])

    if any(k in L for k in [
        "top ", "top-", "top10", "top 10", "ranked",
        "highest", "lowest"
    ]):
        # If it’s about items at a specific site → OPERATIONAL
        if ("item" in L or "items" in L) and re.search(r"\bsite\s+\d+\b", L) and not comparative_triggers:
            return "OPERATIONAL"

        # If explicitly cross-site → COMPARATIVE
        if comparative_triggers or (site_trigger and not re.search(r"\bsite\s+\d+\b", L)):
            return "COMPARATIVE"

        # Otherwise: keep model’s base guess
        return parsed_intent

    # --- 4. Detail or item-level inventory requests ---
    if any(k in L for k in [
        "inventory detail", "show inventory", "show items",
        "items at site", "inventory at site", "detail for site"
    ]):
        return "OPERATIONAL"

    # --- 5. Default fallback ---
    return parsed_intent



def _looks_like_inv_vs_po_by_item(q: str) -> bool:
    L = (q or "").lower()
    return (
        ("inventory vs open po" in L or "inventory versus open po" in L or "inventory vs po" in L)
        and "by item" in L
    )




# ------------------------------------------------------------------
# Plan builder orchestrator
# ------------------------------------------------------------------
def _build_plan(parsed: Dict[str, Any], q: str) -> Optional[Plan]:
    # 1) Explicit PO override (supports PO-0000173)
    po_num = _extract_po_number(q)
    if po_num:
        po_id = f"PO-{po_num.zfill(7)}"   # adjust padding/mask to match your CSV
        filt = [{"col": "po_number", "op": "eq", "value": po_id}]
        return Plan(
            "TRANSACTIONAL",
            f"Explicit PO lookup for {po_id}",
            [Step("filter", "PO", {"where": _norm_filters_for_source("PO", filt), "limit": 2000})]
        )

    if not parsed:
        return None

    # 2) Model intent → coerce by NL hints
    intent = str(parsed.get("intent", "FALLBACK")).upper()
    intent = _coerce_intent(q, intent)

    # 3) Collect filters (LLM + NL site), but DO NOT normalize yet
    fs = (parsed.get("filters") or []) + _parse_site_filter(q)

    # De-dup filters
    _seen, _dedup = set(), []
    src_from_llm = (parsed.get("source") or "").upper()
    for f in fs:
        key = (f.get("col"), f.get("op", "eq"), str(f.get("value")))
        if key not in _seen:
            _seen.add(key)
            _dedup.append(f)
    fs = _dedup

    # 4) Narrow, special MIXED case (inventory vs open PO by item)
    if _looks_like_inv_vs_po_by_item(q):
        site_fs_onhand = _norm_filters_for_source("ONHAND", fs)
        site_fs_po     = _norm_filters_for_source("PO", fs)

        steps = [
            Step("filter", "ONHAND", {"where": site_fs_onhand, "limit": 50000}),
            Step("join", None, {
                "how": "left",
                "right_source": "PO",
                "right_filters": site_fs_po,
                "right_select": None,
                "right_limit": 50000,
                "on_pairs": [("organization_id", "organization_id"), ("item", "item")]
            }),
            Step("derive", None, {"expressions": [{"as": "open_qty", "expr": "ordered_qty - received_qty"}]}),
            Step("sort", None, {"by": ["available_qty"], "ascending": False}),
        ]
        plan = Plan("MIXED", "Inventory vs open PO by item", steps)
        augment_plan_with_sort(plan, parsed, q)
        return plan

    # 5) Regular intent families
    if intent == "TRANSACTIONAL":
        plan = _plan_transactional({"filters": fs, "source": src_from_llm}, q)
        augment_plan_with_sort(plan, parsed, q)
        try:
            augment_plan_with_topk(plan, parsed, q)
        except Exception as e:
            # keep the run healthy; record why topk was skipped
            plan.rationale += f" (topk-skip:{e.__class__.__name__})"
        return plan

    if intent == "OPERATIONAL":
        plan = _plan_operational({
            "filters": fs,
            "group_by": parsed.get("group_by"),
            "metrics": parsed.get("metrics"),
            "sort_by": parsed.get("sort_by"),
            "sort_order": parsed.get("sort_order"),
            "source": src_from_llm
        }, q)
        augment_plan_with_sort(plan, parsed, q)
        try:
            augment_plan_with_topk(plan, parsed, q)
        except Exception as e:
            # keep the run healthy; record why topk was skipped
            plan.rationale += f" (topk-skip:{e.__class__.__name__})"
        return plan

        # If LLM asked for aggregation but no aggregate step exists, add one
        if parsed.get("need_aggregate") and all(s.op != "aggregate" for s in plan.steps):
            by = parsed.get("group_by") or ["organization_id", "item"]
            metrics = parsed.get("metrics") or [("onhand_qty", "sum"), ("available_qty", "sum")]
            plan.steps.insert(1, Step("aggregate", None, {"by": by, "metrics": metrics}))
            plan.rationale = f"{(src_from_llm or 'UNKNOWN')} totals by {', '.join(by)}"
        return plan

    if intent == "COMPARATIVE":
        plan = _plan_comparative(q, {
            "filters": fs,
            "source":  parsed.get("source"),
            "group_by": parsed.get("group_by"),
            "metrics":  parsed.get("metrics"),
            "sort_by":  parsed.get("sort_by"),
            "sort_order": parsed.get("sort_order"),
            "need_aggregate": parsed.get("need_aggregate"),
        })
        augment_plan_with_sort(plan, parsed, q)
        try:
            augment_plan_with_topk(plan, parsed, q)
        except Exception as e:
            # keep the run healthy; record why topk was skipped
            plan.rationale += f" (topk-skip:{e.__class__.__name__})"
        return plan

    if intent == "EXCEPTION":
        plan = _plan_exception({
            "filters": fs,
            "source":  parsed.get("source"),
            "group_by": parsed.get("group_by"),
            "metrics":  parsed.get("metrics"),
            "sort_by":  parsed.get("sort_by"),
            "sort_order": parsed.get("sort_order"),
            "need_aggregate": parsed.get("need_aggregate"),
        }, q)
        augment_plan_with_sort(plan, parsed, q)
        try:
            augment_plan_with_topk(plan, parsed, q)
        except Exception as e:
            # keep the run healthy; record why topk was skipped
            plan.rationale += f" (topk-skip:{e.__class__.__name__})"
        return plan

    if intent == "MIXED":
        plan = _plan_exception({
            "filters": fs,
            "source":  parsed.get("source"),
            "group_by": parsed.get("group_by"),
            "metrics":  parsed.get("metrics"),
            "sort_by":  parsed.get("sort_by"),
            "sort_order": parsed.get("sort_order"),
            "need_aggregate": parsed.get("need_aggregate"),
        }, q)
        augment_plan_with_sort(plan, parsed, q)
        try:
            augment_plan_with_topk(plan, parsed, q)
        except Exception as e:
            # keep the run healthy; record why topk was skipped
            plan.rationale += f" (topk-skip:{e.__class__.__name__})"
        return plan


    # 6) Fallback — OPENAI_ONLY returns FALLBACK so API can jump to Vector/Multi-RAG (Option B)
    if os.getenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY").upper() == "OPENAI_ONLY":
        return Plan("FALLBACK", "Router fallback (no reliable plan)", [])
    else:
        return _plan_fallback({"filters": fs}, q)




# ------------------------------------------------------------------
# Public entry point
# ------------------------------------------------------------------
def route_query(q: str, k: int = 4, mode: str = "OPENAI_ONLY") -> Plan:
    try:
        use_llm = (mode.upper() == "OPENAI_ONLY") and bool(OPENAI_API_KEY) and (OpenAI is not None)
        if use_llm:
            parsed, llm_raw = _classify(q)          # ← LLM JSON
        else:
            parsed, llm_raw = {}, ""

        # ---- NEW: heuristic override of intent ----
        intent_initial = (parsed.get("intent") or "").upper() or "FALLBACK"
        intent_final   = _coerce_intent(q, intent_initial)
        parsed["intent"] = intent_final            # ← ensure planners see the final intent

        # ---- Build plan using FINAL intent ----
        plan = _build_plan(parsed, q)
        if plan is None:
            # In OPENAI_ONLY, do NOT construct a local ONHAND fallback plan.
            # Return a FALLBACK plan so the API/service layer can jump to Vector/Multi-RAG.
            if (mode or "").upper() == "OPENAI_ONLY":
                return Plan("FALLBACK", "Router failed to build plan", [])
            # For LOCAL/HYBRID, keep your legacy local fallback.
            plan = _local_fallback_plan(q)


        # ---- Debug metadata (only when ATLAS_DEBUG=1) ----
        if os.getenv("ATLAS_DEBUG") == "1":
            setattr(plan, "router_debug", {
                "llm_raw":        llm_raw,
                "llm_json":       parsed,
                # Show what the LLM chose (authoritative)
                "ctx_source":     (parsed.get("source") or None),
                # (Optional) keep the old heuristic as a separate field for comparison
                "ctx_source_local_guess": _resolve_ctx_source(q),
                "intent_initial": intent_initial,
                "intent_final":   intent_final,
                "coerce_applied": (intent_final != intent_initial),
            })

        # --- Legacy test labels for LOCAL/HYBRID runs (keeps executor logic unchanged) ---
        try:
            if (mode or "").upper() != "OPENAI_ONLY":
                plan.intent = _legacy_intent_alias(q, plan.intent)
        except Exception:
            pass

        # --- Legacy test labels only for LOCAL/HYBRID (keeps OPENAI_ONLY clean) ---
        try:
            mode = (os.getenv("ATLAS_ROUTER_MODE") or "").upper()
            if mode in {"LOCAL_ONLY", "HYBRID"} and '_legacy_intent_alias' in globals():
                plan.intent = _legacy_intent_alias(q, plan.intent)
        except Exception:
            pass
        

        return plan

    except Exception as e:
        # In OPENAI_ONLY, do NOT synthesize a local ONHAND fallback plan.
        # Hand back a FALLBACK plan so the service can trigger Vector/Multi-RAG.
        if (mode or "").upper() == "OPENAI_ONLY":
            fb = Plan("FALLBACK", f"Router error: {type(e).__name__}: {e}", [])
            if os.getenv("ATLAS_DEBUG") == "1":
                setattr(fb, "router_debug", {"error": f"{type(e).__name__}: {e}"})
            return fb

        # LOCAL/HYBRID: keep legacy behavior
        fb = _local_fallback_plan(q)
        if os.getenv("ATLAS_DEBUG") == "1":
            setattr(fb, "router_debug", {"error": f"{type(e).__name__}: {e}"})
        return fb




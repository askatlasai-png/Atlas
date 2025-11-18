# atlas_plan_executor.py
# v2.2 — CSV-backed Plan Executor (Pandas)
# - Config-driven CSV paths via ATLAS_CSV_CFG (csv_path.json)
# - FILTER / JOIN / AGGREGATE / SORT / TOP_K / DISTINCT
# - Column normalization (aliases + case-insensitive + semantic)
# - Canonicalization for ONHAND (map header variants -> onhand_qty, available_qty)
# - Robust, type-aware filtering in PlanExecutor (so "101" == 101)

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Protocol
import os, time, json, re
# Some blocks use _re; make it an alias to the stdlib 're'
_re = re
import pandas as pd

def _now() -> float:
    return time.time()

def _elapsed_ms(t0: float) -> float:
    return round((time.time() - t0) * 1000, 2)


# ---------- Contracts ----------
@dataclass
class ExecResult:
    rows: List[Dict[str, Any]]
    meta: Dict[str, Any]

class TableAdapter(Protocol):
    def filter(self, params: Dict[str, Any]) -> ExecResult: ...
    def vector(self, params: Dict[str, Any]) -> ExecResult: ...

class Joiner(Protocol):
    def join(self, left: ExecResult, right: ExecResult, on: List[Tuple[str, str]], how: str) -> ExecResult: ...

class Aggregator(Protocol):
    def aggregate(self, res: ExecResult, by: List[str], metrics: List[Tuple[str, str]]) -> ExecResult: ...

# ---------- Guardrails ----------
MAX_ROWS_STEP = 50000
MAX_STEPS     = 16
ALLOWED_SOURCES = {"PO","IR","ONHAND","SO","LPN","LPN_SERIAL","LPN_SERIALS","LPN_SERIALS_AGG","ALL"}
ALLOWED_OPS     = {"filter","vector","aggregate","join","sort","topk","distinct", "derive"}

# Debug-friendly: executor-side clear (noop today)
def clear_executor_caches():
    # If you ever add per-source DF caches, clear them here.
    return


# ---------- CSV registry / aliases ----------
def _load_csv_map() -> Dict[str, str]:
    cfg = os.getenv("ATLAS_CSV_CFG")
    if cfg and os.path.exists(cfg):
        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)

                    # --- plural/singular shims for LPN serial datasets ---
        if "LPN_SERIALS" not in data and "LPN_SERIAL" in data:
            data["LPN_SERIALS"] = data["LPN_SERIAL"]
        if "LPN_SERIAL" not in data and "LPN_SERIALS" in data:
            data["LPN_SERIAL"] = data["LPN_SERIALS"]

        return {
            "PO": data.get("PO"),
            "IR": data.get("IR"),
            "SO": data.get("SO"),
            "ONHAND": data.get("ONHAND"),
            "LPN": data.get("LPN"),
            "LPN_SERIAL": data.get("LPN_SERIAL"),
            "LPN_SERIALS_AGG": data.get("LPN_SERIALS_AGG"),
        }
    # Fallback filenames (relative to ATLAS_DATA_DIR if set)
    return {
        "PO": "v_po_status_enriched.csv",
        "IR": "v_ir_status_enriched.csv",
        "SO": "v_so_delivery_status_enriched.csv",
        "ONHAND": "v_onhand_status_enriched.csv",
        "LPN": "v_lpn_status_se_enriched.csv",
        "LPN_SERIAL": "v_lpn_serials_se_enriched.csv",
        "LPN_SERIALS_AGG": "v_lpn_serials_agg_se_enriched.csv",
    }

DATA_DIR  = os.getenv("ATLAS_DATA_DIR", "./data")
DATASETS  = _load_csv_map()

def _csv_path(source: str) -> str:
    raw = DATASETS.get(source)
    if not raw:
        raise ValueError(f"Unknown source: {source}")
    path = raw if (os.path.isabs(raw) or raw.lower().endswith(".csv")) else os.path.join(DATA_DIR, raw)
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    return path

# Per-source column aliases (router- & executor-side normalization)
COLUMN_ALIASES: Dict[str, Dict[str, str]] = {
    "ONHAND": {
        "sku": "item", "item_id": "item",
        "site": "organization_id", "site_code": "organization_id", "site_id": "organization_id",
        "org": "organization_id", "org_id": "organization_id",
        "onhand": "onhand_qty", "on_hand": "onhand_qty", "onhand_qty": "onhand_qty",
        "available": "available_qty", "availableqty": "available_qty", "available_qty":"available_qty",
        "subinv": "subinventory_code", "subinventory": "subinventory_code",
        "locator": "locator_code",
        "serial": "serial_number",
        "last_update": "last_update_date", "last_updated": "last_update_date",
        "reserved": "reserved_qty", "reservedqty": "reserved_qty", "reserved_qty": "reserved_qty",
        "onhand quantity": "onhand_qty",
        "available quantity": "available_qty",
        "reserved quantity": "reserved_qty",
        "onhand quantity":   "onhand_qty",
        "available quantity":"available_qty",


    },
    "PO": {
        "po": "po_number", "po_no": "po_number", "poid": "po_number",
        "vendor": "vendor_name", "supplier": "vendor_name",
        "eta": "promised_date", "eta_date": "promised_date",
        "needby": "need_by_date", "need_by": "need_by_date",
        "status": "po_status",
        "buyer": "buyer_user_id",
        "item_id": "item", "sku": "item",
        "site": "organization_id", "site_id": "organization_id",
        "org": "organization_id", "org_id": "organization_id",
    },
    "IR": {
        "po": "po_number", "po_no": "po_number",
        "so": "so_number", "so_no": "so_number",
        "status": "req_status",
        "needby": "need_by_date", "need_by": "need_by_date",
        "item_id": "item", "sku": "item",
        "site": "organization_id", "site_id": "organization_id",
        "org": "organization_id", "org_id": "organization_id",
    },
    "SO": {
        "so": "so_number", "so_no": "so_number",
        "customer": "customer_or_site_name", "customer_name": "customer_or_site_name",
        "status": "delivery_status",
        "tracking": "tracking_number", "carrier": "carrier_name",
        "requested_qty": "requested_quantity", "shipped_qty": "shipped_quantity",
        "item_id": "item", "sku": "item",
        "site": "organization_id", "site_id": "organization_id",
        "org": "organization_id", "org_id": "organization_id",
        "from_site": "ship_from_location_id", "to_site": "ship_to_location_id",
    },
    "LPN": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "status": "delivery_status",
        "customer": "customer_or_site_name",
        "from_site": "ship_from_location_id", "to_site": "ship_to_location_id",
        "delivery_detail": "delivery_detail_id",
        "item_id": "item", "sku": "item",
        "site": "organization_id", "site_id": "organization_id",
        "org": "organization_id", "org_id": "organization_id",
    },
    "LPN_SERIAL": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "serial": "serial_number",
        "delivery_detail": "delivery_detail_id",
    },

    "LPN_SERIALS": {
    "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
    "serial": "serial_number",
    "delivery_detail": "delivery_detail_id",
   },

    "LPN_SERIALS_AGG": {
        "lpnid": "lpn_number", "lpn_no": "lpn_number", "lpn": "lpn_number",
        "serials": "serials_csv", "serial_count_total": "serial_count",
        "asset_tag": "asset_tags",
        "delivery": "delivery_number",
    },
}

# ---------------- Column helpers ----------------
def _lower_set(cols): 
    return {str(c).lower() for c in cols}

def _resolve_col_name(df_cols, desired):
    low = str(desired).lower()
    for c in df_cols:
        if str(c).lower() == low:
            return c
    return None

def _map_col(source: str, col: str) -> str:
    return COLUMN_ALIASES.get(source, {}).get(str(col).lower(), col)

def _semantic_candidates(source: Optional[str], desired: str) -> List[str]:
    s = (source or "").upper()
    d = str(desired).lower()
    if s == "ONHAND":
        if d in ("onhand_qty", "onhand"):
            return [
                "onhand_qty","on_hand_qty","on_hand","onhand",
                "qty_on_hand","onhandquantity","on_hand_quantity",
                "total_onhand_qty","total_on_hand","total_on_hand_qty"
            ]
        if d in ("available_qty", "available"):
            return [
                "available_qty","available_quantity","available",
                "qty_available","availableqty","total_available_qty","total_available"
            ]
        if d in ("organization_id","site","org","org_id"):
            return ["organization_id","org_id","site","site_code","org","site_id"]
        if d in ("item","sku","item_id"):
            return ["item","sku","item_id","item number","item_number"]
        if d in ("reserved_qty", "reserved", "reservedqty", "reserved qty", "reserved quantity"):
            return ["reserved_qty", "reservedquantity", "reserved qty", "reserved", "reserved-qty"]

    return []

def _try_semantic(df_cols, candidates: List[str]) -> Optional[str]:
    low = {str(c).lower(): c for c in df_cols}
    for cand in candidates or []:
        if cand.lower() in low:
            return low[cand.lower()]
    return None

def _fuzzy_semantic(df_cols, tokens: List[str]) -> Optional[str]:
    cols = [str(c) for c in df_cols]
    for c in cols:
        lc = c.lower()
        if all(t in lc for t in tokens):
            return c
    return None

def _normalize_cols_for_source(source: Optional[str], df_cols, cols: List[str]) -> List[str]:
    src = source or "ALL"
    out = []
    df_low = _lower_set(df_cols)
    for c in (cols or []):
        aliased = _map_col(src, c) if src in COLUMN_ALIASES else c
        if str(aliased) in df_cols or str(aliased).lower() in df_low:
            ci = _resolve_col_name(df_cols, aliased) or aliased
            out.append(ci); continue
        sem = _try_semantic(df_cols, _semantic_candidates(src, aliased))
        out.append(sem if sem is not None else aliased)
    return out

def _normalize_metrics_for_source(source: Optional[str], df_cols, metrics: List[tuple]) -> List[tuple]:
    fixed = []
    for (col, agg) in metrics or []:
        col2 = _normalize_cols_for_source(source, df_cols, [col])[0]
        fixed.append((col2, agg))
    return fixed

def _canonicalize_df(source: Optional[str], df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str,str]]:
    src = (source or "").upper()
    if src != "ONHAND" or df.empty:
        return df, {}
    renames: Dict[str, str] = {}
    oh = _try_semantic(df.columns, _semantic_candidates("ONHAND", "onhand_qty")) or \
         _fuzzy_semantic(df.columns, ["on","hand"]) or _fuzzy_semantic(df.columns, ["onhand"])
    if oh and oh != "onhand_qty": renames[oh] = "onhand_qty"
    av = _try_semantic(df.columns, _semantic_candidates("ONHAND", "available_qty")) or \
         _fuzzy_semantic(df.columns, ["avail"]) or _fuzzy_semantic(df.columns, ["available"])
    if av and av != "available_qty": renames[av] = "available_qty"
    if renames: df = df.rename(columns=renames)
    return df, renames

# ---------- Real CSV Adapter ----------
class PandasCsvAdapter:
    """Lazy CSV reader; exposes get_df() and simple filter/vector stubs when needed."""
    def __init__(self, source: str, path: str | None = None):
        self.source = source
        self.path   = path or _csv_path(source)
        self._df: Optional[pd.DataFrame] = None

    def _ensure_loaded(self):
        if self._df is not None and len(self._df.index) > 0:
            return
        self._df = pd.read_csv(self.path)
        self._df.name = self.source

    def get_df(self) -> pd.DataFrame:
        self._ensure_loaded()
        return self._df

    # Adapter-level filter is simple; executor will do robust filtering
    def filter(self, params: Dict[str, Any]) -> ExecResult:
        self._ensure_loaded()
        df = self._df
        sel = params.get("select")
        limit = params.get("limit", MAX_ROWS_STEP)
        if sel:
            keep = [c for c in sel if c in df.columns]
            if keep: df = df[keep]
        if limit: df = df.head(int(limit))
        return ExecResult(rows=df.to_dict("records"),
                          meta={"op":"filter","source":self.source,"n":len(df)})

    def vector(self, params: Dict[str, Any]) -> ExecResult:
        # not used here; mirror filter
        return self.filter(params)

# ---------- Join & Aggregate ----------
class PandasJoiner:
    def join(self, left: ExecResult, right: ExecResult, on: List[Tuple[str, str]], how: str = "left") -> ExecResult:
        t0 = time.time()
        left_df  = pd.DataFrame(left.rows)
        right_df = pd.DataFrame(right.rows)
        if left_df.empty or right_df.empty:
            out = left_df if how in ("left","outer") else pd.DataFrame()
        else:
            left_on  = [l for (l, r) in on]
            right_on = [r for (l, r) in on]
            out = left_df.merge(right_df, how=how, left_on=left_on, right_on=right_on)
        return ExecResult(
            rows=out.to_dict(orient="records"),
            meta={"op":"join","how":how,"on":on,"left_n":len(left.rows),"right_n":len(right.rows),
                  "out_n":len(out), "elapsed_ms": round((time.time()-t0)*1000,2)}
        )

class PandasAggregator:
    def aggregate(self, res: ExecResult, by: List[str], metrics: List[Tuple[str, str]]) -> ExecResult:
        t0 = time.time()
        df = pd.DataFrame(res.rows)
        if df.empty:
            return ExecResult(rows=[], meta={"op":"aggregate","by":by,"metrics":metrics,"input_n":0})
        agg_dict = {col: agg for (col, agg) in metrics}
        g = df.groupby(by, dropna=False).agg(agg_dict).reset_index() if by else df.agg(agg_dict).to_frame().T
        return ExecResult(
            rows=g.to_dict(orient="records"),
            meta={"op":"aggregate","by":by,"metrics":metrics,"input_n":len(df),"out_n":len(g),
                  "elapsed_ms": round((time.time()-t0)*1000,2)}
        )

# ---------- Registry ----------
class AdapterRegistry:
    def __init__(self, cfg_path: str | None = None):
        self.cfg_path = cfg_path or os.environ.get("ATLAS_CSV_CFG")
        if not self.cfg_path:
            raise RuntimeError("ATLAS_CSV_CFG env var not set; point it to csv_path.json")

        with open(self.cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

                # --- plural/singular shims for LPN serial datasets ---
        if "LPN_SERIALS" not in cfg and "LPN_SERIAL" in cfg:
            cfg["LPN_SERIALS"] = cfg["LPN_SERIAL"]
        if "LPN_SERIAL" not in cfg and "LPN_SERIALS" in cfg:
            cfg["LPN_SERIAL"] = cfg["LPN_SERIALS"]


        def _getp(name: str) -> Optional[str]:
            return cfg.get(name) or cfg.get(name.lower()) or cfg.get(name.upper())

        self.tables: Dict[str, TableAdapter] = {}
        for src in ALLOWED_SOURCES:
            if src == "ALL": 
                continue
            p = _getp(src)
            if p:
                self.tables[src] = PandasCsvAdapter(src, p)

        if not self.tables:
            raise RuntimeError(f"No CSVs mapped from {self.cfg_path}. Provide at least ONHAND/PO/SO paths.")

        self.joiner = PandasJoiner()
        self.agg    = PandasAggregator()

    def __repr__(self) -> str:
        return f"<AdapterRegistry tables={list(self.tables.keys())}>"

# ---------- Executor ----------
class PlanExecutor:
    def __init__(self, registry: Optional[AdapterRegistry] = None):
        self.r = registry or AdapterRegistry()

    # --- type-aware equality (numeric/string tolerant, case-insensitive for text)
    def _eq_mask(self, series: pd.Series, v: Any) -> pd.Series:
        if pd.api.types.is_numeric_dtype(series.dtype):
            vnum = pd.to_numeric(v, errors="coerce")
            if not pd.isna(vnum):
                return series == vnum
            return series.astype(str) == str(v)
        return series.astype(str).str.casefold() == str(v).casefold()

    # --- robust filter application with aliasing + type-aware ops
    def _apply_filters(self, df: pd.DataFrame, where: List[Dict[str, Any]], source: Optional[str] = None) -> pd.DataFrame:
        """
        Apply a list of filter predicates to df.

        Enhancements:
        • Support {"value":{"colref":"<other_col>"}} to compare column-to-column
        • Date-aware comparisons for both column↔column and column↔scalar predicates
        • Fall back to numeric, then string lexicographic compare when dates not applicable
        """
        src = (source or getattr(df, "name", None) or "ONHAND")
        low = {c.lower(): c for c in df.columns}

        mask = pd.Series(True, index=df.index)
        for f in (where or []):
            raw = f.get("col")
            col = _map_col(src, raw)
            col = low.get(str(col).lower(), col)
            if col not in df.columns:
                raise KeyError(f"[{src}] Column '{raw}' not found after aliasing (wanted '{col}')")

            s = df[col]
            op = (f.get("op") or "eq").lower()
            val = f.get("value")

            # -------- equality / inequality (kept as-is; uses your existing tolerant matcher) --------
            if op in ("eq", "==", "="):
                m = self._eq_mask(s, val)

            elif op in ("ne", "!="):
                m = ~self._eq_mask(s, val)

            # -------- set membership / substring (kept as-is) --------
            elif op == "in":
                vals = f.get("values") or (val if isinstance(val, list) else [val])
                vals_norm = {str(v).casefold() for v in vals}
                m = s.astype(str).str.casefold().isin(vals_norm)

            elif op == "contains":
                m = s.astype(str).str.contains(str(val), case=False, na=False)

            # -------- ordered comparisons (enhanced) --------
            elif op in ("gt", ">", "ge", ">=", "lt", "<", "le", "<="):
                # Case A: RHS is a column reference -> column-to-column compare
                if isinstance(val, dict) and "colref" in val:
                    other_raw = val["colref"]
                    other_col = _map_col(src, other_raw)
                    other_col = low.get(str(other_col).lower(), other_col)
                    if other_col not in df.columns:
                        raise KeyError(f"[{src}] Column '{other_raw}' not found after aliasing (wanted '{other_col}')")

                    s2 = df[other_col]

                    # Try date compare first
                    s_dt  = pd.to_datetime(s,  errors="coerce")
                    s2_dt = pd.to_datetime(s2, errors="coerce")
                    if s_dt.notna().any() or s2_dt.notna().any():
                        a, b = s_dt, s2_dt
                    else:
                        # Try numeric compare
                        a_num = pd.to_numeric(s,  errors="coerce")
                        b_num = pd.to_numeric(s2, errors="coerce")
                        if a_num.notna().any() or b_num.notna().any():
                            a, b = a_num, b_num
                        else:
                            # Fallback: lexicographic on strings
                            a, b = s.astype(str), s2.astype(str)

                # Case B: RHS is a scalar -> column-to-scalar compare (date→numeric→string)
                else:
                    # Try date compare
                    a_dt = pd.to_datetime(s, errors="coerce")
                    b_dt = pd.to_datetime(pd.Series([val]), errors="coerce").iloc[0]
                    if a_dt.notna().any() and pd.notna(b_dt):
                        a, b = a_dt, b_dt
                    else:
                        # Try numeric
                        a_num = pd.to_numeric(s, errors="coerce")
                        b_num = pd.to_numeric(pd.Series([val]), errors="coerce").iloc[0]
                        if a_num.notna().any() and pd.notna(b_num):
                            a, b = a_num, b_num
                        else:
                            # Fallback: lexicographic
                            a, b = s.astype(str), str(val)

                # Execute the ordered comparison with the resolved (a, b)
                if op in ("gt", ">"):
                    m = a > b
                elif op in ("ge", ">="):
                    m = a >= b
                elif op in ("lt", "<"):
                    m = a < b
                else:  # ("le","<=")
                    m = a <= b

            else:
                raise ValueError(f"Unsupported filter op '{op}' in {f}")

            mask &= m.fillna(False)

        return df[mask]


    def run(self, plan) -> Dict[str, Any]:
        t0 = time.time()
        steps = getattr(plan, "steps", [])
        if not steps:
            return {"rows": [], "meta": {"warning":"No steps to execute",
                                         "plan_intent": getattr(plan, 'intent', None),
                                         "plan_rationale": getattr(plan, 'rationale', None)}}
        clipped = False
        if len(steps) > MAX_STEPS:
            steps = steps[:MAX_STEPS]; clipped = True

        last: Optional[ExecResult] = None
        lineage: List[Dict[str, Any]] = []
        current_source: Optional[str] = None

        for idx, s in enumerate(steps, start=1):
            if s.op not in ALLOWED_OPS:
                lineage.append({"step": idx, "error": f"disallowed op {s.op}"}); break
            if getattr(s, "source", None) and s.source not in ALLOWED_SOURCES and s.op in {"filter","vector"}:
                lineage.append({"step": idx, "error": f"unknown source {s.source}"}); break

            t1 = time.time()

            # ---- FILTER / VECTOR ----
            if s.op in {"filter","vector"}:
                adapter = self.r.tables[s.source]
                df0 = adapter.get_df()  # lazy-loads CSV
                df1, _ = _canonicalize_df(s.source, df0)

                where = s.params.get("where") or []
                try:
                    df_out = self._apply_filters(df1, where, s.source)
                except Exception as e:
                    lineage.append({"step": idx, "op": s.op, "source": s.source,
                                    "params": s.params, "error": str(e),
                                    "elapsed_ms": round((time.time()-t1)*1000, 2)})
                    break

                select_cols = s.params.get("select")
                if select_cols:
                    sel_norm = _normalize_cols_for_source(s.source, df_out.columns, select_cols)
                    missing = [c for c in sel_norm if c not in df_out.columns]
                    if missing:
                        lineage.append({"step": idx, "op": s.op, "source": s.source,
                                        "params": s.params, "error": f"select columns missing after normalize: {missing}",
                                        "elapsed_ms": round((time.time()-t1)*1000, 2)})
                        break
                    df_out = df_out[sel_norm]

                limit = s.params.get("limit")
                if limit: df_out = df_out.head(int(limit))

                res = ExecResult(rows=df_out.to_dict("records"),
                                 meta={"op": s.op, "source": s.source, "where": where, "limit": limit})
                current_source = s.source

            # ---- AGGREGATE ----
            elif s.op == "aggregate":
                if last is None:
                    lineage.append({"step": idx, "error":"aggregate with no input"}); break
                df = pd.DataFrame(last.rows)
                df2, _ = _canonicalize_df(current_source, df)
                tmp = ExecResult(rows=df2.to_dict("records"), meta=last.meta)

                by      = s.params.get("by", [])
                metrics = s.params.get("metrics", [])
                by_norm      = _normalize_cols_for_source(current_source, df2.columns, by)
                metrics_norm = _normalize_metrics_for_source(current_source, df2.columns, metrics)

                missing = [c for c in by_norm if c not in df2.columns]
                if missing:
                    lineage.append({"step": idx, "error": f"aggregate group-by columns missing after normalize: {missing}"}); break
                for (c, _) in metrics_norm:
                    if c not in df2.columns:
                        lineage.append({"step": idx, "error": f"aggregate metric column missing after normalize: {c}"}); break

                res = self.r.agg.aggregate(tmp, by_norm, metrics_norm)

            # ---- JOIN ----
            elif s.op == "join":
                if last is None:
                    lineage.append({"step": idx, "error":"join with no left input"}); break
                right_src   = s.params.get("right_source")
                right_where = s.params.get("right_filters", [])
                right_sel   = s.params.get("right_select")
                right_lim   = s.params.get("right_limit", MAX_ROWS_STEP)

                right_adapter = self.r.tables[right_src]
                right = right_adapter.filter({"where": right_where, "select": right_sel, "limit": right_lim})

                pairs = s.params.get("on_pairs")
                left_df  = pd.DataFrame(last.rows)
                right_df = pd.DataFrame(right.rows)
                left_df2, _ = _canonicalize_df(current_source, left_df)
                right_df2, _ = _canonicalize_df(right_src, right_df)

                left_keys, right_keys = [], []
                for (l, r) in pairs:
                    l2 = _normalize_cols_for_source(current_source, left_df2.columns,  [l])[0]
                    r2 = _normalize_cols_for_source(right_src,      right_df2.columns, [r])[0]
                    left_keys.append(l2); right_keys.append(r2)

                miss_l = [c for c in left_keys  if c not in left_df2.columns]
                miss_r = [c for c in right_keys if c not in right_df2.columns]
                if miss_l or miss_r:
                    lineage.append({"step": idx, "error": f"join keys missing after normalize: left={miss_l}, right={miss_r}"}); break

                out_df = left_df2.merge(right_df2, how=s.params.get("how","left"),
                                        left_on=left_keys, right_on=right_keys)
                res = ExecResult(rows=out_df.to_dict("records"),
                                 meta={"op":"join","how":s.params.get("how","left"),
                                       "on": list(zip(left_keys, right_keys)),
                                       "left_n": len(left_df2), "right_n": len(right_df2), "out_n": len(out_df)})
                current_source = "ALL"

            # ---- DERIVE ----
            elif s.op == "derive":
                if last is None:
                    lineage.append({"step": idx, "error": "derive with no input"}); break
                df = pd.DataFrame(last.rows)
                df2, _ = _canonicalize_df(current_source, df)
                exprs = s.params.get("expressions") or []
                try:
                    for e in exprs:
                        out_col = e.get("as")
                        expr    = (e.get("expr") or "").strip()
                        if not out_col or not expr:
                            continue
                        # VERY simple parser: support "<colA> - <colB>" / "<colA> + <colB>"
                        m = re.match(r"^\s*([A-Za-z0-9_]+)\s*([+\-*/])\s*([A-Za-z0-9_]+)\s*$", expr)
                        if not m:
                            raise ValueError(f"unsupported derive expr: {expr!r}")
                        a, op, b = m.group(1), m.group(2), m.group(3)
                        # normalize input column names
                        a_norm = _normalize_cols_for_source(current_source, df2.columns, [a])[0]
                        b_norm = _normalize_cols_for_source(current_source, df2.columns, [b])[0]
                        if a_norm not in df2.columns or b_norm not in df2.columns:
                            raise KeyError(f"derive columns missing after normalize: {a_norm}, {b_norm}")
                        sA = pd.to_numeric(df2[a_norm], errors="coerce").fillna(0)
                        sB = pd.to_numeric(df2[b_norm], errors="coerce").fillna(0)
                        if   op == "-": df2[out_col] = sA - sB
                        elif op == "+": df2[out_col] = sA + sB
                        elif op == "*": df2[out_col] = sA * sB
                        elif op == "/": df2[out_col] = sA.replace(0, pd.NA) / sB.replace(0, pd.NA)
                    res = ExecResult(rows=df2.to_dict("records"), meta={"op":"derive","n":len(df2)})
                except Exception as e:
                    lineage.append({"step": idx, "op": "derive", "source": getattr(s,"source",current_source),
                                    "params": s.params, "error": str(e),
                                    "elapsed_ms": round((time.time()-t1)*1000,2)})
                    break

            # ---- SORT ----
            # ---- SORT ----
            elif s.op == "sort":
                t_sort0 = time.time()

                # ✅ Change #1: handle "sort with no input" as a no-op up front
                if last is None:
                    lineage.append({
                        "step": idx, "op": "sort",
                        "source": getattr(s, "source", current_source),
                        "params_in": s.params,
                        "by_resolved": None,
                        "order_final": None,
                        "ascending_resolved": None,
                        "rows_after_step": 0,
                        "elapsed_ms": 0.0
                    })
                    last = ExecResult(rows=[], meta={"op":"sort","by":None,"ascending":None,"limit":s.params.get("limit")})
                    continue

                # ✅ Change #2: pre-init locals so 'except' can safely reference them
                by_col = None
                ascending = None
                order_param = (s.params.get("sort_order") or s.params.get("order") or "").strip().lower()
                ord_word = ""

                try:
                    # Load current rows and canonicalize ONHAND headers where needed
                    df = pd.DataFrame(last.rows)

                    # NEW: if there are 0 rows, keep it a no-op (don’t fail the plan)
                    if df.empty:
                        res = ExecResult(rows=[], meta={"op":"sort","by":None,"ascending":None,"limit":s.params.get("limit")})
                        lineage.append({
                            "step": idx, "op": "sort",
                            "source": getattr(s, "source", current_source),
                            "params_in": s.params,
                            "by_resolved": None,
                            "order_final": None,
                            "ascending_resolved": None,
                            "rows_after_step": 0,
                            "elapsed_ms": 0.0
                        })
                        last = res
                        continue

                    df2, _ = _canonicalize_df(current_source, df)

                    # ---- SORT (LLM-first; regex fallback) ----
                    llm_sort_by = s.params.get("sort_by")
                    order_param = (s.params.get("sort_order") or s.params.get("order") or "").strip().lower()
                    raw_by      = s.params.get("by")
                    if isinstance(raw_by, list) and raw_by:
                        raw_by = raw_by[0]

                    # 1) Resolve sort-by column
                    if llm_sort_by:
                        base_by  = str(llm_sort_by).strip()
                        ord_word = ""   # direction will come from sort_order/order
                    else:
                        if not raw_by:
                            # treat as a no-op sort
                            res = ExecResult(rows=df2.to_dict("records"),
                                            meta={"op":"sort","by":None,"ascending":None,"limit":s.params.get("limit")})
                            lineage.append({
                                "step": idx, "op": "sort",
                                "source": getattr(s, "source", current_source),
                                "params_in": s.params,
                                "by_resolved": None,
                                "order_final": None,
                                "ascending_resolved": None,
                                "rows_after_step": len(df2),
                                "elapsed_ms": 0.0
                            })
                            last = res
                            continue
                        raw_by_str = str(raw_by).strip()
                        # accept optional trailing 'order' e.g. "reserved_qty descending order"
                        m = _re.match(r"^(.*?)(?:\s+(ascending|descending|asc|desc)(?:\s+order)?)?\s*$",
                                      raw_by_str, _re.IGNORECASE)
                        base_by  = (m.group(1) or "").strip()
                        ord_word = ((m.group(2) or "").strip().lower())
                        # drop stray trailing literal "order"
                        base_by  = _re.sub(r"\border\b$", "", base_by, flags=_re.IGNORECASE).strip()

                    # Alias/canonicalize column
                    _alias = COLUMN_ALIASES.get(current_source, {})
                    k1 = base_by.lower()
                    k2 = _re.sub(r'[\s\-_]+', '', k1)
                    by_col = _alias.get(k1) or _alias.get(k2) or base_by
                    # normalize against actual df2 columns (semantic if needed)
                    by_col = _normalize_cols_for_source(current_source, df2.columns, [by_col])[0]
                    if by_col not in df2.columns:
                        raise KeyError(f"sort column missing after normalize: wanted={base_by!r}, got={by_col!r}")

                    # 2) Resolve direction (embedded word wins, then params, else fallback)
                    asc_field = s.params.get("ascending", None)

                    # ord_word was extracted from the 'by' text (e.g., "... descending order")
                    # order_param came from s.params['sort_order'] or ['order'] (LLM/router)
                    if   ord_word in ("desc","descending"):    order = "desc"; order_source = "embedded"
                    elif ord_word in ("asc","ascending"):      order = "asc";  order_source = "embedded"
                    elif order_param in ("desc","descending"): order = "desc"; order_source = "sort_order"
                    elif order_param in ("asc","ascending"):   order = "asc";  order_source = "sort_order"
                    else:
                        order = None; order_source = None

                    if   order == "desc": ascending = False
                    elif order == "asc":  ascending = True
                    else:
                        if isinstance(asc_field, bool):
                            ascending = asc_field
                        elif isinstance(asc_field, str):
                            ascending = asc_field.strip().lower() in ("1","true","t","yes","y")
                        else:
                            ascending = True

                    # 3) Sort (stable) and optional limit — numeric-aware
                    col_ser = df2[by_col]
                    as_num  = pd.to_numeric(col_ser, errors="coerce")

                    if as_num.notna().any():
                        tmp = df2.assign(__k__=as_num)
                        out = tmp.sort_values(by="__k__", ascending=ascending, kind="mergesort").drop(columns="__k__")
                    else:
                        out = df2.sort_values(by=by_col, ascending=ascending, kind="mergesort")

                    limit = s.params.get("limit")
                    if limit:
                        out = out.head(int(limit))

                    # 4) Build result and lineage, then continue
                    res = ExecResult(
                        rows=out.to_dict(orient="records"),
                        meta={"op":"sort","by":by_col,"ascending":ascending,"limit":limit}
                    )
                    dt = time.time() - t_sort0
                    lineage.append({
                        "step": idx,
                        "op": "sort",
                        "source": getattr(s, "source", current_source),
                        "params_in": s.params,
                        "by_resolved": by_col,
                        "order_final": ("desc" if not ascending else "asc"),
                        "order_param_in": order_param or None,
                        "embedded_order_in": ord_word or None,
                        "order_source": order_source,
                        "ascending_resolved": ascending,
                        "rows_after_step": len(out),
                        "elapsed_ms": round(dt*1000, 2)
                    })

                    last = res
                    continue

                except Exception as e:
                    dt = time.time() - t_sort0
                    lineage.append({
                        "step": idx,
                        "op": "sort",
                        "source": getattr(s, "source", current_source),
                        "params_in": s.params,
                        "by_resolved": by_col,                 # now always defined (None ok)
                        "order_in": order_param or ord_word or None,
                        "ascending_resolved": ascending,       # now always defined (None ok)
                        "rows_after_step": len(last.rows) if last else 0,
                        "elapsed_ms": round(dt*1000, 2),
                        "error": f"{type(e).__name__}: {e}"
                    })
                    break




            # ---- TOP_K ----
            # ---- TOPK ----
            # ---- TOPK ----
            elif s.op == "topk":
                # params: {"by": "<col>" or ["<col>"], "k": int, "ascending": bool}
                t0 = _now()

                if last is None:
                    lineage.append({"step": idx, "error": "topk with no input"})
                    break

                # Load current rows and canonicalize ONHAND headers where needed
                df = pd.DataFrame(last.rows)
                df2, _ = _canonicalize_df(current_source, df)

                params = s.params or {}
                k   = int(params.get("k", 10))
                by  = params.get("by")
                asc = bool(params.get("ascending", False))  # default False => "top" = highest first

                # Normalize "by" (user may pass list or string)
                if isinstance(by, list):
                    by = by[0] if by else None

                by_col = None
                if by:
                    # Map to canonical/internal column name
                    by_norm_list = _normalize_cols_for_source(current_source, df2.columns, [by])
                    by_col = by_norm_list[0] if by_norm_list else None
                    if not by_col or by_col not in df2.columns:
                        raise KeyError(f"topk column missing after normalize: wanted={by!r}, got={by_col!r}")

                    # --- numeric-aware, stable sort (mirrors 'sort' op) ---
                    col_ser = df2[by_col]
                    as_num  = pd.to_numeric(col_ser, errors="coerce")
                    if as_num.notna().any():
                        tmp = df2.assign(__k__=as_num)
                        df2 = tmp.sort_values(by="__k__", ascending=asc, kind="mergesort").drop(columns="__k__")
                    else:
                        df2 = df2.sort_values(by=by_col, ascending=asc, kind="mergesort")

                # take top K after (optional) sort
                out = df2.head(k).reset_index(drop=True)

                # Build result and enriched lineage (like 'sort')
                res = ExecResult(
                    rows=out.to_dict(orient="records"),
                    meta={"op": "topk", "by": by_col, "ascending": asc, "k": k}
                )
                lineage.append({
                    "step": idx,
                    "op": "topk",
                    "source": getattr(s, "source", current_source),
                    "params_in": s.params,
                    "by_resolved": by_col,
                    "ascending_resolved": bool(asc),
                    "k": int(k),
                    "rows_after_step": len(out),
                    "elapsed_ms": _elapsed_ms(t0),
                })
                last = res
                continue



            # ---- DISTINCT ----
            elif s.op == "distinct":
                if last is None:
                    lineage.append({"step": idx, "error": "distinct with no input"}); break
                df = pd.DataFrame(last.rows)
                df2, _ = _canonicalize_df(current_source, df)
                cols = s.params.get("cols")
                if cols:
                    cols_norm = _normalize_cols_for_source(current_source, df2.columns, cols)
                    missing = [c for c in cols_norm if c not in df2.columns]
                    if missing:
                        lineage.append({"step": idx, "error": f"distinct columns missing after normalize: {missing}"}); break
                    out = df2.drop_duplicates(subset=cols_norm)
                else:
                    out = df2.drop_duplicates()
                res = ExecResult(rows=out.to_dict("records"),
                                 meta={"op":"distinct","cols":cols or "ALL"})

            else:
                lineage.append({"step": idx, "error":"unsupported op"}); break

            dt = time.time() - t1
            if len(res.rows) > MAX_ROWS_STEP:
                res.rows = res.rows[:MAX_ROWS_STEP]
                res.meta["warning"] = f"rows clipped to {MAX_ROWS_STEP}"
            lineage.append({"step": idx, "op": s.op, "source": getattr(s, "source", current_source),
                            "params": s.params, "rows_after_step": len(res.rows), "elapsed_ms": round(dt*1000,2)})
            last = res

        return {
            "rows": last.rows if last else [],
            "meta": {
                "plan_intent": getattr(plan, 'intent', None),
                "plan_rationale": getattr(plan, 'rationale', None),
                "lineage": lineage,
                "clipped": clipped,
                "elapsed_ms": round((time.time()-t0)*1000, 2)
            }
        }

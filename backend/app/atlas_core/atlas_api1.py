# atlas_api.py
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import pandas as pd
# add:
from fastapi.middleware.cors import CORSMiddleware



from atlas_core.atlas_service import run_query as router_run_query

# NEW: import the Multi-RAG adapter (works with your current file layout)
try:
    from multi_rag_cli import run_multi_rag
except Exception:
    try:
        from atlas_core.multi_rag_cli import run_multi_rag
    except Exception:
        run_multi_rag = None  # we'll handle gracefully

app = FastAPI(title="Atlas API (Router + CSV Executor)", version="0.6.0")

from fastapi.middleware.cors import CORSMiddleware

# accept any localhost/127.0.0.1 with any port (dev only)
LOCAL_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=LOCAL_REGEX,     # <- replace allow_origins=[...]
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)



# Default router mode: OPENAI_ONLY (safe if already set)
os.environ.setdefault("ATLAS_ROUTER_MODE", "OPENAI_ONLY")

# --- request model ---
class QueryReq(BaseModel):
    q: str
    k: int = 4
    mode: str | None = "OPENAI_ONLY"
    # NEW:
    augment: bool = False
    session: str | None = None
    preview: bool = False


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "mode": os.getenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY")}

# --- /query handler ---
@app.post("/query")
def query(req: QueryReq) -> Dict[str, Any]:
    try:
        resp = router_run_query(req.q.strip(), k=req.k, mode=req.mode)

        # --- LLM augmentation (always safe; never breaks response) ---
        if getattr(req, "augment", False):
            print(f"[AtlasAPI] augment=True for: {req.q[:80]!r}")

            # Always compute these from the executor result we already have
            rows = resp.get("rows") or []
            meta = resp.get("meta", {}) or {}
            lineage = (meta.get("lineage") or [])[:]
            cols = []
            if rows:
                # union of keys across rows to avoid hiding columns
                seen = {}
                for r in rows:
                    for k in (r or {}).keys():
                        seen.setdefault(k, True)
                cols = list(seen.keys())

            # Prefer formatting from structured rows; if empty, use FAISS Multi-RAG fallback
            try:
                from openai import OpenAI
                from multi_rag_cli import build_system_preamble, format_ctx, answer_question  # reuse style & fallback
            except Exception:
                build_system_preamble = None
                format_ctx = None
                answer_question = None

            answer_text, ctx_preview = None, None

            try:
                if rows:
                    # ---------- Structured rows → LLM formatting ----------
                    if not build_system_preamble:
                        raise RuntimeError("build_system_preamble not importable")

                    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    sys_msg = build_system_preamble()

                    # keep prompt compact but faithful
                    MAX_ROWS_IN_PROMPT = int(os.getenv("ATLAS_LLM_ROWS_MAX", "200"))
                    # render a lightweight, LLM-friendly table
                    def _rows_to_md(rows, cols, k):
                        if not rows:
                            return "(No rows.)"
                        cols = cols or list({c for r in rows for c in (r or {}).keys()})
                        head = "| " + " | ".join(cols) + " |"
                        sep  = "| " + " | ".join(["---"] * len(cols)) + " |"
                        body = []
                        for r in rows[:k]:
                            body.append("| " + " | ".join(str((r or {}).get(c, "")) for c in cols) + " |")
                        more = f"\n\n(Showing first {min(k, len(rows))} of {len(rows)} rows.)" if len(rows) > k else ""
                        return "\n".join([head, sep, *body]) + more

                    table_block = _rows_to_md(rows, cols, MAX_ROWS_IN_PROMPT)

                    # include short lineage breadcrumb (op, source, rows_after_step)
                    L = []
                    for step in lineage[-8:]:
                        op = step.get("op") or step.get("error") or "?"
                        src = step.get("source")
                        n   = step.get("rows_after_step")
                        L.append(f"- {op} @ {src or 'ALL'} → rows={n}")
                    lineage_block = "\n".join(L) if L else "None"

                    user_msg = (
                        f"User Question (standalone): {req.q.strip()}\n\n"
                        f"Structured Result (from executor):\n{table_block}\n\n"
                        f"Lineage (last steps):\n{lineage_block}\n\n"
                        "Now answer using Markdown with these sections:\n"
                        "### Summary\n### Key Facts\n### Details\n### Evidence\n### Next steps\n"
                        "Be concise and factual. Use only the Structured Result for facts. If any key field is missing, say so."
                    )

                    resp_llm = client.chat.completions.create(
                        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
                        messages=[
                            {"role": "system", "content": sys_msg},
                            {"role": "user",   "content": user_msg},
                        ],
                        temperature=0.2,
                        max_tokens=900,
                    )
                    answer_text = (resp_llm.choices[0].message.content or "").strip()
                    meta["approximate"] = False
                    meta.setdefault("badges", []).append("EXACT_STRUCTURED")
                    meta["augment_debug"] = {
                        "context_rows": len(rows),
                        "columns_in_context": cols[:10],
                        "lineage_steps": len(lineage),
                        "vector_used": False,
                        "mode": "rows→LLM"
                    }

                else:
                    # ---------- Zero rows → FAISS Multi-RAG fallback ----------
                    if not answer_question:
                        raise RuntimeError("multi_rag_cli.answer_question not importable")

                    ans, ctx_blocks = answer_question(
                        req.q.strip(),
                        session=(getattr(req, "session", None) or "public"),
                        preview=bool(getattr(req, "preview", False)),
                        api_key=os.getenv("OPENAI_API_KEY"),
                    )
                    answer_text = ans or "(No answer.)"
                    ctx_preview = "\n\n".join(ctx_blocks or [])
                    meta["approximate"] = True
                    meta.setdefault("badges", []).append("APPROXIMATE")
                    meta["rag_ctx_preview"] = ctx_preview
                    meta["augment_debug"] = {
                        "context_rows": 0,
                        "columns_in_context": [],
                        "lineage_steps": len(lineage),
                        "vector_used": True,
                        "mode": "faiss→LLM"
                    }

            except Exception as e:
                meta["rag_error"] = f"{type(e).__name__}: {e}"
                if not answer_text:
                    answer_text = "(augmentation failed)"

            resp["answer"] = answer_text
            resp["meta"] = meta


        return resp

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"query failed: {e}")

    

@app.get("/schema/{source}")
def schema(source: str):
    from atlas_core.atlas_plan_executor import DATASETS
    src = source.upper()
    path = DATASETS.get(src)
    if not path:
        raise HTTPException(status_code=404, detail=f"Unknown source: {src}")
    try:
        cols = pd.read_csv(path, nrows=0).columns.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV for {src}: {e}")
    return {"source": src, "path": path, "columns": cols}


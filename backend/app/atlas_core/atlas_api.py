# atlas_api.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv

# Load environment variables (.env) so OPENAI_API_KEY etc. are available
load_dotenv(find_dotenv(), override=False)

from atlas_core.atlas_service import run_query as router_run_query

# Try to import multi_rag helpers (used only in augment branch / fallback)
try:
    from multi_rag_cli import build_system_preamble, format_ctx, answer_question  # type: ignore
except Exception:
    try:
        from atlas_core.multi_rag_cli import (  # type: ignore
            build_system_preamble,
            format_ctx,
            answer_question,
        )
    except Exception:
        build_system_preamble = None
        format_ctx = None
        answer_question = None


app = FastAPI(title="Atlas API (Router + CSV Executor)", version="0.6.0")

# --- CORS: allow localhost + your Amplify frontend ---
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://staging.de0bq9sp1wzmp.amplifyapp.com",
    "https://atlasaicopilot.com",  # root domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.atlasaicopilot\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)
# Default router mode
os.environ.setdefault("ATLAS_ROUTER_MODE", "OPENAI_ONLY")


# --- Request models ---

class QueryReq(BaseModel):
    q: str
    k: int = 4
    mode: Optional[str] = "OPENAI_ONLY"
    augment: bool = False
    session: Optional[str] = None
    preview: bool = False


class ChatReq(BaseModel):
    question: str
    session: Optional[str] = "public"
    preview: bool = False
    augment: bool = True          # default to True so you get nice NL answers
    k: int = 4
    mode: Optional[str] = None    # let router default if None


# --- Health ---

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "mode": os.getenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY")}


# --- Core executor endpoint ---

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
            cols: list[str] = []
            if rows:
                # union of keys across rows to avoid hiding columns
                seen: Dict[str, bool] = {}
                for r in rows:
                    for k in (r or {}).keys():
                        seen.setdefault(k, True)
                cols = list(seen.keys())

            # Prefer formatting from structured rows; if empty, use FAISS Multi-RAG fallback
            try:
                from openai import OpenAI
            except Exception:
                OpenAI = None  # type: ignore

            answer_text: Optional[str] = None
            ctx_preview: Optional[str] = None

            try:
                if rows:
                    # ---------- Structured rows ? LLM formatting ----------
                    if not build_system_preamble or not OpenAI:
                        raise RuntimeError("build_system_preamble or OpenAI not importable")

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
                        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
                        body = []
                        for r in rows[:k]:
                            body.append(
                                "| "
                                + " | ".join(str((r or {}).get(c, "")) for c in cols)
                                + " |"
                            )
                        more = (
                            f"\n\n(Showing first {min(k, len(rows))} of {len(rows)} rows.)"
                            if len(rows) > k
                            else ""
                        )
                        return "\n".join([head, sep, *body]) + more

                    table_block = _rows_to_md(rows, cols, MAX_ROWS_IN_PROMPT)

                    # include short lineage breadcrumb (op, source, rows_after_step)
                    L = []
                    for step in lineage[-8:]:
                        op = step.get("op") or step.get("error") or "?"
                        src = step.get("source")
                        n = step.get("rows_after_step")
                        L.append(f"- {op} @ {src or 'ALL'} ? rows={n}")
                    lineage_block = "\n".join(L) if L else "None"

                    user_msg = (
                        f"User Question (standalone): {req.q.strip()}\n\n"
                        f"Structured Result (from executor):\n{table_block}\n\n"
                        f"Lineage (last steps):\n{lineage_block}\n\n"
                        "Now answer using Markdown with these sections:\n"
                        "### Summary\n### Key Facts\n### Details\n### Evidence\n### Next steps\n"
                        "Be concise and factual. Use only the Structured Result for facts. "
                        "If any key field is missing, say so."
                    )

                    resp_llm = client.chat.completions.create(
                        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
                        messages=[
                            {"role": "system", "content": sys_msg},
                            {"role": "user", "content": user_msg},
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
                        "mode": "rows?LLM",
                    }

                else:
                    # ---------- Zero rows ? FAISS Multi-RAG fallback ----------
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
                        "mode": "faiss?LLM",
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


# --- /api/chat wrapper for frontend ---

@app.post("/api/chat")
async def chat_api(req: ChatReq) -> Dict[str, Any]:
    """
    Thin wrapper so the frontend can keep using /api/chat while we route
    through the structured CSV executor (/query) pipeline.
    """
    q_req = QueryReq(
        q=req.question,
        k=req.k,
        mode=req.mode or os.getenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY"),
        augment=req.augment,
        session=req.session,
        preview=req.preview,
    )

    resp = query(q_req)  # type: ignore[arg-type]

    meta = resp.get("meta") or {}
    rows = resp.get("rows") or []
    answer = resp.get("answer")

    if not answer:
        if rows:
            answer = (
                f"Found {len(rows)} matching rows. "
                "Enable augment=True for a natural language summary."
            )
        else:
            answer = "No matching records found."

    ctx_preview = meta.get("rag_ctx_preview")
    if not ctx_preview:
        if rows:
            cols = list({c for r in rows for c in (r or {}).keys()})
            head = "| " + " | ".join(cols) + " |"
            sep = "| " + " | ".join(["---"] * len(cols)) + " |"
            body = []
            for r in rows[:10]:
                body.append(
                    "| "
                    + " | ".join(str((r or {}).get(c, "")) for c in cols)
                    + " |"
                )
            more = (
                f"\n\n(Showing first {min(10, len(rows))} of {len(rows)} rows.)"
                if len(rows) > 10
                else ""
            )
            ctx_preview = "\n".join([head, sep, *body]) + more
        else:
            ctx_preview = "(No context rows.)"

    return {
        "answer": answer,
        "context": ctx_preview,
        "rows": rows,
        "meta": meta,
    }

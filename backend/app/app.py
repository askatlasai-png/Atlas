# app.py — FastAPI wrapper around multi_rag_cli.py

import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Response



# ⬇️ import helpers from your CLI file
from multi_rag_cli import (
    load_indexes,
    ConversationStore,
    condense_query_with_llm,
    format_history_for_prompt,
    format_ctx,
    HISTORY_TURNS,
    CODE_RX,
    MAX_CTX_DOCS,
    build_system_preamble,
    OpenAI,
    CHAT_MODEL,
)

from dotenv import load_dotenv
load_dotenv()  # <-- loads .env into process env

ALLOW_ORIGINS = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()]
# TEMP: log what the app actually sees
print("ALLOW_ORIGINS =", ALLOW_ORIGINS)


# ---- Config via env vars ----
INDEXES_CFG = os.getenv("INDEXES_CFG", "indexes.json")  # path to your indexes.json
CHAT_HISTORY_PATH = os.getenv("CHAT_HISTORY_PATH", "chat_history.jsonl")
#ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "http://localhost:5173").split(",")
ATLAS_API_KEY = os.getenv("ATLAS_API_KEY", "")  # optional demo key

# ---- Init app + CORS ----
app = FastAPI(title="Atlas API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Warm indexes + stores at startup (fast subsequent requests) ----
stores, exact_maps = load_indexes(INDEXES_CFG)
store = ConversationStore(CHAT_HISTORY_PATH)
client = OpenAI()


class ChatReq(BaseModel):
    question: str
    session: str = "public"
    preview: bool = False


@app.post("/api/chat")
def chat(req: ChatReq, x_atlas_key: str = Header(default="")):
    # Basic demo auth (optional)
    if ATLAS_API_KEY and x_atlas_key != ATLAS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    q = (req.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty question")

    # Save user msg, pull recent turns, condense
    store.append(req.session, "user", q)
    pairs = store.last_turns(req.session, HISTORY_TURNS)
    condensed_q = condense_query_with_llm(client, pairs, q)

    # -------- Retrieval: exact + vector across all stores --------
    tokens = [t.upper() for t in CODE_RX.findall(condensed_q)]
    exact_blocks = []
    for label, m in exact_maps.items():
        for t in tokens:
            if t in m:
                exact_blocks.append((label, m[t], 0.0))

    vec_hits = []
    for label, vs in stores.items():
        for d, dist in vs.similarity_search_with_score(condensed_q, k=40):
            vec_hits.append((label, d.page_content, float(dist)))
    vec_hits.sort(key=lambda x: x[2])

    merged, seen = [], set()
    for triple in exact_blocks + vec_hits:
        label, text, score = triple
        key = (label, text[:400])
        if key in seen:
            continue
        seen.add(key)
        merged.append(triple)
        if len(merged) >= MAX_CTX_DOCS:
            break

    if not merged:
        return {"answer": "No matching context found.", "context": ""}

    ctx_block = "\n\n".join([format_ctx(lbl, txt, sc) for lbl, txt, sc in merged])

    # Preview mode: send only the retrieved context back to UI
    if req.preview:
        return {"answer": "(preview mode — no answer)", "context": ctx_block}

    # -------- Compose prompt + ask model --------
    sys_msg = build_system_preamble()
    user_msg = f"""Conversation Context:
{format_history_for_prompt(pairs)}

@app.options("/api/chat")
def chat_preflight() -> Response:
    return Response(status_code=200)

User Question (standalone): {condensed_q}

Retrieved Context:
{ctx_block}

Answer concisely using only the retrieved context. If details are missing, say what's missing and the next step."""
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    answer = resp.choices[0].message.content.strip()
    store.append(req.session, "assistant", answer)
    return {"answer": answer, "context": ctx_block}

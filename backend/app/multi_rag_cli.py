import os, json, re, argparse, datetime, textwrap, csv
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI

# -------- Config --------
DEFAULT_BOT_NAME = os.environ.get("ERP_BOT_NAME", "Atlas")
MAX_CTX_DOCS = 60
MAX_CHARS_PER_DOC = 900
ANSWER_STYLE = "both"
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
HISTORY_PATH = os.environ.get("CHAT_HISTORY_PATH", "chat_history.jsonl")
HISTORY_TURNS = 6
CONDENSE_WITH_LLM = True

# -------- Utilities --------
DASHES = "[\u2010\u2011\u2012\u2013\u2014\u2212\u00ad]"
DASH_RX = re.compile(DASHES)
CODE_RX = re.compile(
    r"\b(?:PO|SO|REQ|IR|LPN|ITEM|DEL|SHIP|INV|ASN)[-_]?[A-Z0-9]{3,}\b", re.I
)

# -------- Global reverse indexes --------
# tn -> list of (label, value_blob)
GLOBAL_TN_MAP: Dict[str, List[Tuple[str, str]]] = {}
# user id -> list of (dataset_label, record_blob)
GLOBAL_USER_MAP: Dict[str, List[Tuple[str, str]]] = {}

# Tracking number patterns
TN_UPS   = re.compile(r"\b1Z[0-9A-Z]{16}\b", re.I)
TN_FEDEX = re.compile(r"\b\d{12}\b|\b\d{15}\b|\b\d{20}\b")
TN_USPS  = re.compile(r"\b\d{20,22}\b")
TN_LINE_RX = re.compile(r"^\s*tracking_number\s*:\s*(.+?)\s*$", re.I | re.M)

# User ID extraction from value blobs
USER_LINE_RX = re.compile(
    r"^\s*(?:ordered_by_user_id|requested_by_user_id|created_by|user_id)\s*:\s*([0-9A-Z_-]{4,20})\s*$",
    re.I | re.M,
)


def has_strong_entity(q: str) -> bool:
    """Return True if the query contains PO/SO/DEL/LPN/ITEM, TN, or USER id tokens."""
    if CODE_RX.search(q):
        return True
    if TN_UPS.search(q) or TN_FEDEX.search(q) or TN_USPS.search(q):
        return True
    # loose user token check (same logic used in gather_hits)
    raw_tokens = re.findall(r"[0-9A-Z_-]+", q.upper())
    for tok in raw_tokens:
        if norm_user(tok) in GLOBAL_USER_MAP:
            return True
    return False


_RUNTIME = None  # (client, stores, exact_maps)

def norm_user(u: str) -> str:
    return ''.join(str(u).upper().strip().split())

def norm_tn(s: str) -> str:
    return ''.join(str(s).upper().split()).replace('-', '')

def _abs_path(base_file: str, maybe_rel: str) -> str:
    if os.path.isabs(maybe_rel):
        return maybe_rel
    base_dir = os.path.dirname(os.path.abspath(base_file))
    return os.path.abspath(os.path.join(base_dir, maybe_rel))

def trim(s: str, limit: int) -> str:
    s = s.strip()
    if len(s) <= limit:
        return s
    return s[:limit] + "…"


# -------- Conversation Store --------
@dataclass
class Message:
    ts: str
    session_id: str
    role: str
    content: str


class ConversationStore:
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            open(self.path, "a").close()

    def append(self, session_id: str, role: str, content: str):
        msg = Message(
            ts=datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            session_id=session_id,
            role=role,
            content=content,
        )
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg.__dict__, ensure_ascii=False) + "\n")

    def load(self, session_id: str) -> List[Message]:
        if not os.path.exists(self.path):
            return []
        out: List[Message] = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("session_id") == session_id:
                        out.append(Message(**rec))
                except Exception:
                    continue
        return out

    def last_turns(self, session_id: str, k_turns: int) -> List[Tuple[str, str]]:
        msgs = self.load(session_id)
        pairs: List[Tuple[str, str]] = []
        cur_user: Optional[str] = None
        for m in msgs:
            if m.role == "user":
                cur_user = m.content
            elif m.role == "assistant" and cur_user is not None:
                pairs.append((cur_user, m.content))
                cur_user = None
        return pairs[-k_turns:]


# -------- Index loading --------
def load_indexes(cfg_path: str) -> Tuple[Dict[str, FAISS], Dict[str, Dict[str, str]]]:
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    emb = OpenAIEmbeddings(model=EMBED_MODEL)
    stores: Dict[str, FAISS] = {}
    exact_maps: Dict[str, Dict[str, str]] = {}

    # clear global maps in case of reload
    GLOBAL_TN_MAP.clear()
    GLOBAL_USER_MAP.clear()

    for label, base_dir in cfg.items():
        faiss_dir = os.path.join(base_dir, "faiss_index")
        if not os.path.isdir(faiss_dir):
            print(f"[WARN] Skipping {label}: missing {faiss_dir}")
            continue
        try:
            stores[label] = FAISS.load_local(
                faiss_dir, emb, allow_dangerous_deserialization=True
            )
            print(f"[OK] Loaded {label} index from {faiss_dir}")
        except Exception as e:
            print(f"[WARN] Could not load {label}: {e}")

        exact_path = os.path.join(base_dir, "exact_lookup.json")
        if os.path.exists(exact_path):
            try:
                with open(exact_path, "r", encoding="utf-8") as f2:
                    m = json.load(f2)

                # Build normal exact map (PO/SO/DEL/LPN/ITEM)
                key_map = {str(k).upper(): str(v) for k, v in m.items()}
                exact_maps[label] = key_map

                # Initialize counters BEFORE loops
                added_tn = 0
                added_user = 0

                for _, v in m.items():
                    v_s = str(v)

                    # ---- TRACKING NUMBERS ----
                    for tn_raw in TN_LINE_RX.findall(v_s):
                        t = norm_tn(tn_raw)
                        if not t:
                            continue
                        GLOBAL_TN_MAP.setdefault(t, []).append((label, v_s))
                        added_tn += 1

                    # ---- USER IDs ----
                    for u_raw in USER_LINE_RX.findall(v_s):
                        u = norm_user(u_raw)
                        if not u:
                            continue
                        GLOBAL_USER_MAP.setdefault(u, []).append((label, v_s))
                        added_user += 1

                print(
                    f"[OK] Loaded exact map for {label} with {len(m):,} entries | "
                    f"TN_refs_added_to_global={added_tn} | USER_refs_added_to_global={added_user}"
                )

            except Exception as e:
                print(f"[WARN] Could not load exact_lookup for {label}: {e}")
        else:
            exact_maps[label] = {}

    return stores, exact_maps


# -------- Master CSV (for examples) --------
def load_master_ids(csv_path: Optional[str], max_ids: int = 5) -> List[str]:
    ids: List[str] = []
    if not csv_path or not os.path.exists(csv_path):
        return ids
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                for c in [
                    "item",
                    "item_id",
                    "inventory_item_id",
                    "sku",
                    "item_number",
                    "ITEM",
                    "SKU",
                ]:
                    if c in row and row[c]:
                        ids.append(str(row[c]).strip())
                        break
                if len(ids) >= max_ids:
                    break
    except Exception:
        pass
    return ids

def _get_runtime():
    """
    Initialize once per process. Needs:
      - OPENAI_API_KEY in env
      - INDEXES_CFG pointing to indexes.json
    """
    global _RUNTIME
    if _RUNTIME is not None:
        return _RUNTIME

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    cfg_path = os.getenv("INDEXES_CFG")
    if not cfg_path:
        raise RuntimeError("INDEXES_CFG not set (path to indexes.json)")
    cfg_path = os.path.abspath(cfg_path)
    if not os.path.isfile(cfg_path):
        raise RuntimeError(f"indexes.json not found at: {cfg_path}")

    client = OpenAI(api_key=api_key)
    stores, exact_maps = load_indexes(cfg_path)
    _RUNTIME = (client, stores, exact_maps)
    print(f"[Atlas] Runtime ready: {len(stores)} FAISS index(es) from {cfg_path}")
    return _RUNTIME


# -------- Greeting / banner --------
def sample_prompts(labels: List[str], example_items: List[str]) -> List[str]:
    S: List[str] = []
    if "PO" in labels:
        S.append("Status of PO-0000155 and expected receipt date")
    if "SO" in labels:
        S.append("Show delivery status for SO-0000144 by line")
    if "ONHAND" in labels:
        if example_items:
            S.append(f"On-hand vs reserved for item {example_items[0]}")
        else:
            S.append("On-hand vs reserved for ITEM-00149")
    if "LPN" in labels or "LPN_SER" in labels:
        S.append("Which items and serials are in LPN-0000178?")
    if "IR" in labels:
        S.append("Open internal requisitions for ITEM-00098")
    S.append("What’s in the package with tracking number 1Z576292076981747?")
    S.append("Summarize late deliveries in the last 7 days")
    return S[:6]


def banner(name: str, labels: List[str], example_items: List[str]) -> str:
    lines = []
    lines.append("═" * 72)
    lines.append(f" {name} — Intelligent ERP + Supply Chain Copilot")
    lines.append("═" * 72)
    lines.append(
        "Welcome! I’m Atlas — designed to help you explore ERP, supply chain, and inventory data using natural language."
    )
    lines.append("")
    lines.append(
        "Connected datasets: " + (", ".join(labels) if labels else "(none loaded)")
    )
    if example_items:
        lines.append("Sample items: " + ", ".join(example_items))
    lines.append("")
    lines.append("Try asking:")
    for sp in sample_prompts(labels, example_items):
        lines.append("  • " + sp)
    lines.append("  • help  — show this menu again")
    lines.append("  • exit  — quit session")
    lines.append("-")
    return "\n".join(lines)


# -------- Retrieval --------
def keyword_hits(vs: FAISS, q: str, k: int = 40) -> List[Tuple[str, float]]:
    docs = vs.similarity_search_with_score(q, k=k)
    return [(d.page_content, score) for d, score in docs]


# -------- Query condensation --------
def format_history_for_condense(pairs: List[Tuple[str, str]]) -> str:
    lines = []
    for i, (q, a) in enumerate(pairs, 1):
        lines.append(f"Turn {i}\nUser: {q}\nAssistant: {a}")
    return "\n\n".join(lines)


def condense_query_with_llm(
    client: OpenAI, history_pairs: List[Tuple[str, str]], question: str
) -> str:
    if not history_pairs:
        return question
    prompt = (
        "You are a query rewriter for an ERP RAG assistant.\n"
        "Rewrite the user's latest follow-up as a fully self-contained, unambiguous query,\n"
        "using the provided conversation history for context. Keep domain terms exact (PO, SO, LPN, etc.).\n"
        "Do not answer the question. Output only the rewritten query.\n\n"
        f"Conversation History:\n{format_history_for_condense(history_pairs)}\n\n"
        f"User question: {question}\n\nRewritten query:"
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()


# -------- Prompt construction --------
def build_system_preamble() -> str:
    return (
        "You are Atlas, an ERP + supply-chain copilot. Answer ONLY from the retrieved context.\n"
        "Always reply in clean GitHub-flavored Markdown with this exact structure:\n"
        "## Summary\n"
        "- 1–3 bullets with the direct answer.\n"
        "## Key Facts\n"
        "- Short bullet list of the most important fields (ID, status, dates, qty, org, subinventory, etc.).\n"
        "## Details (table if applicable)\n"
        "| Field | Value |\n"
        "|------:|:------|\n"
        "(include a compact table of relevant fields if you have them; otherwise 2–4 bullets)\n"
        "## Evidence (from context)\n"
        "- Quote or reference exact IDs, lines, or dates verbatim.\n"
        "## Next steps\n"
        "- 1–2 bullets for what to ask or check if something is missing.\n"
        "\n"
        "Rules:\n"
        "- Keep domain terms exact (PO, SO, LPN, ONHAND, IR).\n"
        "- If data is missing, say so explicitly in Summary and Next steps.\n"
        "- No speculation. No external knowledge. No repeating the whole context.\n"
    )


def format_history_for_prompt(pairs: List[Tuple[str, str]]) -> str:
    if not pairs:
        return ""
    lines = ["Recent conversation (for context):"]
    for q, a in pairs[-HISTORY_TURNS:]:
        lines.append(f"- Q: {trim(q, 300)}")
        lines.append(f"  A: {trim(a, 400)}")
    return "\n".join(lines)


def format_ctx(label: str, txt: str, score: float) -> str:
    return f"[{label} | score={score:.3f}]\n" + trim(
        txt.replace("\n\n", "\n"), MAX_CHARS_PER_DOC
    )


# -------- Retrieval core --------
def gather_hits(
    stores: Dict[str, FAISS],
    exact_maps: Dict[str, Dict[str, str]],
    q: str,
    k: int = 40,
) -> List[Tuple[str, str, float]]:
    """Exact-lookup merge + vector search, deduped, capped by MAX_CTX_DOCS."""

    # A) Direct ID tokens (PO/SO/DEL/LPN/ITEM…)
    tokens = [t.upper() for t in CODE_RX.findall(q)]

    # B) Loose tracking numbers in the query
    tn_candidates: List[str] = []
    for rx in (TN_UPS, TN_FEDEX, TN_USPS):
        tn_candidates.extend(rx.findall(q))
    tn_candidates = [norm_tn(t) for t in tn_candidates]

    # C) Loose user IDs in the query (tokenize and keep those present in the global map)
    raw_tokens = re.findall(r"[0-9A-Z_-]+", q.upper())
    user_candidates: List[str] = []
    for tok in raw_tokens:
        u = norm_user(tok)
        if u in GLOBAL_USER_MAP:
            user_candidates.append(u)
    # de-dup while preserving order
    user_candidates = list(dict.fromkeys(user_candidates))

    # Router debug
    print(f"[exact-router] q='{q}' ids={tokens} tn={tn_candidates} users={user_candidates}")

    # ---- Exact hits (IDs + TNs + USERs) ----
    exact_blocks: List[Tuple[str, str, float]] = []

    # A1) ID-style exacts from per-label exact_maps
    if tokens:
        for label, m in exact_maps.items():
            for t in tokens:
                if t in m:
                    exact_blocks.append((label, m[t], 0.0))

    # A2) Tracking-number exacts from GLOBAL_TN_MAP (across all datasets)
    for t in tn_candidates:
        for (src_label, rec) in GLOBAL_TN_MAP.get(t, []):
            exact_blocks.append((src_label, rec, 0.0))

    # A3) User-ID exacts from GLOBAL_USER_MAP (across all datasets)
    for u in user_candidates:
        for (src_label, rec) in GLOBAL_USER_MAP.get(u, []):
            exact_blocks.append((src_label, rec, 0.0))

    # B) Vector fallback
    vec_hits: List[Tuple[str, str, float]] = []
    for label, vs in stores.items():
        try:
            docs = vs.similarity_search_with_score(q, k=k)
            for d, dist in docs:
                vec_hits.append((label, d.page_content, float(dist)))
        except Exception as e:
            print(f"[WARN] Vector search failed for {label}: {e}")

    vec_hits.sort(key=lambda x: x[2])

    # C) Merge (exact first), de-dup by (label, first 400 chars)
    merged: List[Tuple[str, str, float]] = []
    seen = set()
    for triple in exact_blocks + vec_hits:
        label, text, score = triple
        key = (label, text[:400])
        if key in seen:
            continue
        seen.add(key)
        merged.append(triple)
        if len(merged) >= MAX_CTX_DOCS:
            break
    return merged


# -------- Chat loop (CLI) --------
def chat_loop(
    indexes_cfg: str,
    k: int,
    session_id: str,
    preview: bool,
    name: str,
    master_csv: Optional[str],
    no_greeting: bool,
):
    client = OpenAI()
    store = ConversationStore(HISTORY_PATH)
    stores, exact_maps = load_indexes(indexes_cfg)
    labels = list(stores.keys())
    ex_items = load_master_ids(master_csv)

    if not no_greeting:
        print(banner(name, labels, ex_items))

    print("Type a question (or 'exit'):")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye")
            break
        if not q or q.lower() in {"exit", "quit", "q"}:
            break

        if q.lower() in {"help", "?", "menu"}:
            print("\n" + banner(name, labels, ex_items) + "\n")
            continue

        store.append(session_id, "user", q)
        pairs = store.last_turns(session_id, HISTORY_TURNS)
        condensed_q = q
        if CONDENSE_WITH_LLM and not has_strong_entity(q):
            condensed_q = condense_query_with_llm(client, pairs, q)


        # ===== Gather docs via unified path =====
        top_hits = gather_hits(stores, exact_maps, condensed_q, k=k)

        if not top_hits:
            print(
                "\nNo matching context found. Check ID spelling or indexes.json paths.\n"
            )
            continue

        if preview:
            print("\n--- Context Preview ---")
            for lbl, txt, sc in top_hits[:10]:
                print(f"[{lbl}] score={sc:.3f}\n{trim(txt, 300)}\n")
            print("(Preview mode: no model call)\n")
            continue

        hist_block = format_history_for_prompt(pairs)
        ctx_block = "\n\n".join([format_ctx(lbl, txt, sc) for lbl, txt, sc in top_hits])

        sys_msg = build_system_preamble()
        user_msg = f"""Conversation Context:
{format_history_for_prompt(pairs)}

User Question (standalone): {condensed_q}

Retrieved Context (RAG):
{ctx_block}

Now answer using the required Markdown structure (Summary, Key Facts, Details, Evidence, Next steps).
If a section is not applicable, keep the heading and write "None". Keep it concise and factual."""

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
        print("\n" + answer + "\n")
        store.append(session_id, "assistant", answer)


# -------- FastAPI adapter helpers --------
def run_multi_rag(
    question: str,
    session: str = "public",
    preview: bool = False,
    api_key: Optional[str] = None,
):
    """
    Adapter for FastAPI. Must return (answer_text, context_text).
    """
    answer_text, ctx_blocks = answer_question(
        question, session=session, preview=preview, api_key=api_key
    )
    context_text = "\n\n".join(ctx_blocks)
    return answer_text, context_text


def answer_question(
    question: str, session: str = "public", preview: bool = False, api_key: Optional[str] = None
):
    """
    Returns (answer_text, ctx_blocks_list).
    Uses FAISS retrieval + optional query condensation + OpenAI completion.
    """
    # 1) runtime (OpenAI client + indexes)
    client, stores, exact_maps = _get_runtime()

    # 2) memory (short rolling history)
    mem = ConversationStore(HISTORY_PATH)
    mem.append(session, "user", question)
    history = mem.last_turns(session, HISTORY_TURNS)

    # 3) make follow-ups standalone (conditional — skip if query already has entity)
    final_q = question
    if CONDENSE_WITH_LLM and not has_strong_entity(question):
        final_q = condense_query_with_llm(client, history, question)


    # 4) retrieve (exact ID hits + TN + USER + vector search, deduped)
    hits = gather_hits(stores, exact_maps, final_q, k=40)
    if not hits:
        return (
            "I couldn’t find matching context for that question. Check ID spelling or refresh the indexes.",
            []
        )

    # 5) preview mode returns context only (no LLM call)
    if preview:
        preview_blocks = [format_ctx(lbl, txt, sc) for lbl, txt, sc in hits[:10]]
        return "(Preview mode — showing retrieved context only.)", preview_blocks

    # 6) build prompt (system + user with history + RAG context)
    sys_msg = build_system_preamble()
    ctx_block = "\n\n".join(format_ctx(lbl, txt, sc) for lbl, txt, sc in hits)
    convo_block = format_history_for_prompt(history)
    user_msg = (
        f"Conversation Context:\n{convo_block}\n\n"
        f"User Question (standalone): {final_q}\n\n"
        f"Retrieved Context (RAG):\n{ctx_block}\n\n"
        "Now answer using Markdown with these sections:\n"
        "### Summary\n### Key Facts\n### Details\n### Evidence\n### Next steps\n"
        "Be concise and factual. Cite IDs explicitly in Evidence. If a section is N/A, write 'None'."
    )

    # 7) LLM call
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=900,
    )
    answer = (resp.choices[0].message.content or "").strip()

    # 8) save assistant turn & prepare side-pane context
    mem.append(session, "assistant", answer)
    ctx_blocks = [format_ctx(lbl, txt, sc) for lbl, txt, sc in hits[:8]]

    return answer, ctx_blocks


# -------- CLI --------
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="ERP RAG CLI with conversation memory")
    p.add_argument("--indexes_cfg", required=True, help="Path to indexes.json file")
    p.add_argument("--k", type=int, default=40, help="Top-K retrieval")
    p.add_argument("--session", default="default", help="Session ID")
    p.add_argument(
        "--preview",
        action="store_true",
        help="Show retrieved context without model call",
    )
    p.add_argument(
        "--name", default=DEFAULT_BOT_NAME, help="Bot display name in greeting banner"
    )
    p.add_argument(
        "--master_csv",
        default=None,
        help="Optional CSV to pull sample item IDs for prompts",
    )
    p.add_argument(
        "--no_greeting",
        action="store_true",
        help="Suppress the greeting banner on start",
    )
    args = p.parse_args()

    chat_loop(
        args.indexes_cfg,
        args.k,
        args.session,
        args.preview,
        args.name,
        args.master_csv,
        args.no_greeting,
    )

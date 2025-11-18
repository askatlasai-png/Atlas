# rag_cli.py
import os, argparse, json, re
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

DASHES = "[\u2010\u2011\u2012\u2013\u2014\u2212\u00ad]"
DASH_RX = re.compile(DASHES)
MAX_CTX_DOCS = 50  # send up to this many docs to the LLM
MAX_CHARS_PER_DOC = 800  # trim each doc to keep prompt lean
ANSWER_STYLE = "both"  # "bullets", "sentence", or "both"

# ---- Suggestion settings ----
SUGGESTION_LIMIT = 5
SUGGEST_MODE = "heuristic"  # "heuristic", "llm", or "both"


def suggest_questions_heuristic(
    q: str, tokens: list[str], loaded_labels: list[str]
) -> list[str]:
    ql = q.lower()
    S = []

    # Item-centric
    if "item" in ql or any(t.startswith("ITEM-") for t in tokens):
        S += [
            "Show purchase orders for this item",
            "Show sales orders for this item",
            "Which LPNs currently hold this item?",
            "What is the on-hand and reserved qty for this item?",
            "Any open internal requisitions for this item?",
        ]

    # Document-centric (REQ/PO/SO)
    if any(t.startswith(("REQ-", "PO-", "SO-")) for t in tokens):
        S += [
            "Show header and line details for this document",
            "What is the current status and next action?",
            "Which item and quantity does it involve?",
            "What dates are associated (need-by / promise / ship)?",
            "Show related upstream/downstream documents",
        ]

    # LPN
    if "lpn" in ql or any("LPN" in t for t in tokens):
        S += [
            "Which items are in this LPN?",
            "What subinventory/locator is this LPN in?",
            "Show serials in this LPN",
            "Show recent moves for this LPN",
        ]

    # Gate suggestions by which datasets are actually loaded
    label_gate = {
        "Show purchase orders for this item": "PO",
        "Show sales orders for this item": "SO",
        "Which LPNs currently hold this item?": "LPN",
        "What is the on-hand and reserved qty for this item?": "ONHAND",
        "Any open internal requisitions for this item?": "IR",
        "Show serials in this LPN": "LPN_SER",
    }
    loaded = set(loaded_labels)
    S = [s for s in S if label_gate.get(s) in loaded or label_gate.get(s) is None]

    # Unique + cap
    out = []
    for s in S:
        if s not in out:
            out.append(s)
        if len(out) >= SUGGESTION_LIMIT:
            break
    return out


def llm_suggestions(client, chat_model: str, q: str, answer: str) -> list[str]:
    prompt = (
        "Given the question and the answer, suggest 3–5 short follow-up questions "
        "that would help an ERP analyst go deeper. Keep each under 12 words. "
        "Do not repeat the original question.\n\n"
        f"Question: {q}\nAnswer:\n{answer}\n\nFollow-ups:"
    )
    resp = client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    lines = [
        l.strip("-• ").strip()
        for l in resp.choices[0].message.content.splitlines()
        if l.strip()
    ]
    out = []
    for l in lines:
        if l and l not in out:
            out.append(l)
        if len(out) >= SUGGESTION_LIMIT:
            break
    return out


def norm_text(s: str) -> str:
    s = s.replace("\u200b", "")
    s = DASH_RX.sub("-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


CODE_RX = re.compile(r"\b[A-Z]{2,6}-?\d{3,}\b", re.I)


def keyword_hits(vs, q, k=8):
    # pull a generous candidate set, then filter
    docs = vs.similarity_search(q, k=max(k, 40))
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9_\-]{4,}", q)  # catches REQ-0000316
    if not tokens:
        return docs[:k]
    scored = []
    for d in docs:
        t = d.page_content
        score = sum(1 for tok in tokens if tok in t)
        if score > 0:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in (scored[:k] or [(0, x) for x in docs[:k]])]


def exact_lookup_first(q: str, exact_map: dict, k: int):
    tokens = [t.upper() for t in CODE_RX.findall(norm_text(q))]
    hits = []
    for t in tokens:
        if t in exact_map:
            hits.append(exact_map[t])
    # return up to k exact hits as fake docs (text only), else empty
    return hits[:k]


SYSTEM_PROMPT = """You are an ERP + Supply Chain assistant.
Answer ONLY from the provided context. Aggregate all relevant rows for the asked ID/code or item.
If nothing is in context, say so without guessing. Prefer concise answers."""


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--index_dir", required=True, help="Folder that contains faiss_index"
    )
    p.add_argument("--k", type=int, default=6)
    p.add_argument(
        "--answer", action="store_true", help="Synthesize an answer with OpenAI"
    )
    p.add_argument("--embed_model", default="text-embedding-3-small")
    p.add_argument("--chat_model", default="gpt-4o-mini")
    args = p.parse_args()

    # index_dir points to ...\erp_index\faiss_index
    # exact map was saved one level up (out_dir)
    exact_path = os.path.normpath(
        os.path.join(args.index_dir, "..", "exact_lookup.json")
    )
    exact_map = {}
    if os.path.exists(exact_path):
        with open(exact_path, "r", encoding="utf-8") as f:
            exact_map = json.load(f)

    emb = OpenAIEmbeddings(model=args.embed_model)
    vs = FAISS.load_local(args.index_dir, emb, allow_dangerous_deserialization=True)
    loaded_labels = ["MASTER"]  # or whatever label you want to display for this index

    print("Type a question (or 'exit'):")
    client = OpenAI() if args.answer else None
    while True:
        q = input("> ").strip()
        if q.lower() in {"exit", "quit"} or not q:
            break

        # ---- find entity tokens (ID/item codes) and normalize ----
        tokens = [t.upper() for t in CODE_RX.findall(norm_text(q))]

        # ---- collect exact hits (all of them), if any ----
        exact_hits = []
        for t in tokens:
            if t in exact_map:
                exact_hits.append(exact_map[t])

        # ---- collect vector hits, then filter to include rows that mention any token ----
        vec_docs = keyword_hits(
            vs, q, k=args.k
        )  # pull a larger candidate set inside fn
        vec_hits = []
        if tokens:
            for d in vec_docs:
                txt = d.page_content
                if any(tok in txt.upper() for tok in tokens):
                    vec_hits.append(txt)
        else:
            vec_hits = [d.page_content for d in vec_docs]

        # ---- merge, dedupe, trim, and cap ----
        def trim(s):
            s = s.replace("\n\n", "\n").strip()
            return s[:MAX_CHARS_PER_DOC] + (
                " ..." if len(s) > MAX_CHARS_PER_DOC else ""
            )

        merged = []
        seen = set()
        for block in exact_hits + vec_hits:
            key = block[:400]  # cheap stable dedupe
            if key not in seen:
                seen.add(key)
                merged.append(trim(block))
            if len(merged) >= MAX_CTX_DOCS:
                break

        # ---- display what we’re sending ----
        if exact_hits:
            print(f"\nExact ID hits: {len(exact_hits)}")
            for i, t in enumerate(exact_hits[:10], 1):
                print(f"[E{i}] {t[:220]}...")
        print(f"\nVector matches used: {max(0, len(merged) - len(exact_hits))}")

        # ---- build answer instruction: bullets + sentence (or as chosen) ----
        if ANSWER_STYLE == "both":
            style_hint = (
                "Return two parts:\n"
                "1) Bulleted list of all relevant orders/records found.\n"
                "2) One concise summary sentence capturing the key takeaway."
            )
        elif ANSWER_STYLE == "sentence":
            style_hint = "Return a single concise sentence summarizing the findings."
        else:
            style_hint = "Return a concise bulleted list of the findings."

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT + "\n"
                "Use ONLY the provided context. Aggregate across ALL matching rows (don’t stop at the first). "
                "Group by order type (PO/SO/IR) when possible. Do not invent details.\n"
                + style_hint,
            },
            {
                "role": "user",
                "content": "# Context\n"
                + "\n\n---\n".join(merged)
                + f"\n\n# Question\n{q}\n\n# Answer:",
            },
        ]

        answer_text = ""
        if args.answer:
            try:
                client = OpenAI()
                resp = client.chat.completions.create(
                    model=args.chat_model, messages=messages, temperature=0.0
                )
                answer_text = resp.choices[0].message.content.strip()
                print("\nAnswer:\n" + answer_text)
            except Exception as e:
                print(f"\nAnswer generation failed: {e}")

        # ---- Suggested follow-up questions ----
        sugs = []
        if SUGGEST_MODE in {"heuristic", "both"}:
            sugs.extend(suggest_questions_heuristic(q, tokens, loaded_labels))
        if SUGGEST_MODE in {"llm", "both"} and args.answer and answer_text:
            try:
                sugs_llm = llm_suggestions(client, args.chat_model, q, answer_text)
                for s in sugs_llm:
                    if s not in sugs and len(sugs) < SUGGESTION_LIMIT:
                        sugs.append(s)
            except Exception as e:
                print(f"(Follow-up suggestions via LLM failed: {e})")

        if sugs:
            print("\nTry next:")
            for i, s in enumerate(sugs, 1):
                print(f"  {i}. {s}")

        print("")


if __name__ == "__main__":
    main()

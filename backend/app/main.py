import time, sys, os, traceback

print("=== main.py: starting FastAPI init ===")
print("cwd:", os.getcwd())
print("Python path:", sys.path)
start_time = time.time()

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv, find_dotenv

print("=== main.py: importing multi_rag_cli ===")
try:
    from .multi_rag_cli import run_multi_rag  # adjust if needed
    print("=== main.py: imported multi_rag_cli successfully ===")
except Exception as e:
    print(f"=== main.py: failed to import multi_rag_cli: {e} ===")
    run_multi_rag = None

# Load environment variables
print("=== main.py: loading .env ===")
load_dotenv(find_dotenv(), override=False)

# Initialize FastAPI
app = FastAPI(title="Atlas Backend", version="1.0")

# Configure CORS
print("=== main.py: configuring CORS ===")
ALLOW_ORIGINS = [
    o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS or ["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # includes X-Atlas-Key
)

class ChatReq(BaseModel):
    question: str
    session: Optional[str] = "public"
    preview: Optional[bool] = False

DEBUG = os.getenv("DEBUG", "0") == "1"

@app.get("/healthz")
def healthz():
    print("=== /healthz called ===")
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_api(
    req: ChatReq,
    x_atlas_key: Optional[str] = Header(default=None, alias="X-Atlas-Key")
):
    print(f"=== /api/chat received: {req.question} ===")
    try:
        if run_multi_rag:
            # Real RAG pipeline
            answer_text, context_text = run_multi_rag(
                question=req.question,
                session=req.session,
                preview=req.preview
            )
        else:
            # Fallback for debugging
            answer_text = f"(fallback) Echo: {req.question}"
            context_text = "(demo) multi_rag_cli not loaded"

        print("=== /api/chat returning response ===")
        return {"answer": answer_text, "context": context_text}

    except Exception as e:
        tb = traceback.format_exc()
        print("\n=== chat_api ERROR ===\n", tb)
        msg = f"{e.__class__.__name__}: {e}"
        if DEBUG:
            # In dev, show details in UI so we can diagnose fast
            return {"answer": f"[DEV] {msg}", "context": tb}
        raise HTTPException(status_code=500, detail="Internal Server Error")

print(f"=== main.py: FastAPI app initialized in {time.time() - start_time:.2f}s ===")

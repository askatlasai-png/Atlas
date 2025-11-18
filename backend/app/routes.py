# app/routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.post("/chat")
async def chat(req: dict):
    # TODO: call your existing chat core function
    return {"ok": True}

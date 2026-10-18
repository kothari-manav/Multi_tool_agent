import logging
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import run_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="CogniSphere Agent API")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    tools_used: list[str]
    session_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    try:
        result = run_agent(req.message, session_id)
    except Exception:
        logger.exception("Agent failed")
        raise HTTPException(status_code=502, detail="The assistant failed to respond. Please try again.")
    return ChatResponse(**result, session_id=session_id)
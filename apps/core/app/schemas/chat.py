from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    session_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str | None = None

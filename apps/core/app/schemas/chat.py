from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    session_id: str | None = None
    user_id: str | None = None
    store_id: str | None = Field(
        None,
        description="Optional store UUID to scope the commerce agent context",
    )


class ChatResponse(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str | None = None

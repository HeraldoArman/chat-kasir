from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService


class HealthResponse(BaseModel):
    status: str


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    service = ChatService()
    response = await service.process(request)
    return response

import os

import httpx

from app.core.config import get_config
from app.core.exceptions import LLMException
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    def __init__(self) -> None:
        self.config = get_config()
        self.llm_config = self.config.llm

    async def process(self, request: ChatRequest) -> ChatResponse:
        api_key = os.getenv("DEEPINFRA_API_KEY", "")
        if not api_key:
            raise LLMException("DEEPINFRA_API_KEY not configured")

        try:
            async with httpx.AsyncClient(timeout=self.llm_config.timeout) as client:
                response = await client.post(
                    f"{self.llm_config.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.llm_config.model,
                        "messages": [{"role": "user", "content": request.message}],
                        "temperature": self.llm_config.temperature,
                        "max_tokens": self.llm_config.max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return ChatResponse(
                    message=data["choices"][0]["message"]["content"],
                    session_id=request.session_id,
                    user_id=request.user_id,
                )
        except httpx.HTTPStatusError as e:
            raise LLMException(f"LLM request failed: {e}") from e
        except Exception as e:
            raise LLMException(f"Unexpected error: {e}") from e

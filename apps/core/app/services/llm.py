"""LLM Strategy Pattern: DeepSeek primary, Gemini fallback."""

import os
from abc import ABC, abstractmethod

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_full_jitter

from app.core.config import get_config
from app.core.exceptions import LLMException
from app.schemas.chat import ChatRequest, ChatResponse

log = structlog.get_logger()


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError


class DeepInfraProvider(LLMProvider):
    def __init__(self) -> None:
        self.config = get_config()
        self.llm_config = self.config.llm

    @retry(stop=stop_after_attempt(3), wait=wait_full_jitter(max=10))
    async def complete(self, request: ChatRequest) -> ChatResponse:
        api_key = os.getenv("DEEPINFRA_API_KEY", "")
        if not api_key:
            raise LLMException("DEEPINFRA_API_KEY not configured")

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


class GeminiProvider(LLMProvider):
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_MODEL = "gemini-2.0-flash-lite"

    @retry(stop=stop_after_attempt(3), wait=wait_full_jitter(max=10))
    async def complete(self, request: ChatRequest) -> ChatResponse:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise LLMException("GEMINI_API_KEY not configured")

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.GEMINI_BASE_URL}/models/{self.GEMINI_MODEL}:generateContent",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                params={"key": api_key},
                json={
                    "contents": [{"parts": [{"text": request.message}]}],
                },
            )
            response.raise_for_status()
            data = response.json()
            return ChatResponse(
                message=data["candidates"][0]["content"]["parts"][0]["text"],
                session_id=request.session_id,
                user_id=request.user_id,
            )


class LLMService:
    def __init__(self) -> None:
        self.primary = DeepInfraProvider()
        self.fallback = GeminiProvider()

    async def process(self, request: ChatRequest) -> ChatResponse:
        try:
            log.info("llm_request_primary", provider="deepinfra")
            return await self.primary.complete(request)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                log.warning("llm_rate_limited_primary", provider="deepinfra")
            else:
                log.error("llm_error_primary", provider="deepinfra", error=str(e))
            return await self._fallback(request)
        except Exception as e:
            log.error("llm_error_primary", provider="deepinfra", error=str(e))
            return await self._fallback(request)

    async def _fallback(self, request: ChatRequest) -> ChatResponse:
        try:
            log.info("llm_request_fallback", provider="gemini")
            return await self.fallback.complete(request)
        except Exception as e:
            log.error("llm_error_fallback", provider="gemini", error=str(e))
            raise LLMException(f"Both primary and fallback LLM failed: {e}") from e

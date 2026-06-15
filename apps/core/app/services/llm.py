"""OpenAI LLM factory using LangChain."""

import os

import structlog
from langchain_openai import ChatOpenAI

from app.core.config import get_config
from app.core.exceptions import LLMException

log = structlog.get_logger()


class LLMService:
    """Thin factory that returns a configured ChatOpenAI instance."""

    def __init__(self) -> None:
        self.config = get_config()
        self.llm_config = self.config.llm

    def get_chat_model(self) -> ChatOpenAI:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise LLMException("OPENAI_API_KEY not configured")

        return ChatOpenAI(
            model=self.llm_config.model,
            api_key=api_key,
            base_url=self.llm_config.base_url,
            temperature=self.llm_config.temperature,
            max_tokens=self.llm_config.max_tokens,
            timeout=self.llm_config.timeout,
            streaming=False,
        )

    @staticmethod
    def requires_api_key() -> bool:
        return bool(os.getenv("OPENAI_API_KEY", ""))

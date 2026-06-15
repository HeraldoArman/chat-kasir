"""Chat service that delegates to the LangGraph commerce agent."""

from uuid import UUID

import structlog

from app.agent.executor import AgentExecutor
from app.core.exceptions import LLMException
from app.db.session import async_session_factory
from app.models.commerce import Store
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.store import StoreService

log = structlog.get_logger()


class ChatService:
    def __init__(self) -> None:
        self.agent = AgentExecutor()

    async def process(self, request: ChatRequest) -> ChatResponse:
        """Process an HTTP chat message scoped to an optional store."""
        store = await self._resolve_store(request.store_id)
        if store is None:
            return ChatResponse(
                message="Silakan pilih toko terlebih dahulu agar saya bisa membantu.",
                session_id=request.session_id,
                user_id=request.user_id,
            )

        try:
            reply = await self.agent.run(
                message=request.message,
                store=store,
                customer_phone="web-chat",
                customer_name=None,
                is_merchant=False,
            )
        except LLMException:
            raise
        except Exception as e:
            log.error("chat_agent_error", error=str(e))
            raise LLMException(f"Agent error: {e}") from e

        return ChatResponse(
            message=reply,
            session_id=request.session_id,
            user_id=request.user_id,
        )

    async def _resolve_store(self, store_id_str: str | None) -> Store | None:
        if not store_id_str:
            return None
        try:
            store_uuid = UUID(store_id_str)
        except ValueError:
            return None
        async with async_session_factory() as db:
            store_service = StoreService(db)
            return await store_service.get_by_id(store_uuid)

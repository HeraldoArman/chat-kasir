"""High-level executor that wires a user message through the commerce agent graph.

Usage::

    from app.agent.executor import AgentExecutor

    executor = AgentExecutor()
    reply = await executor.run(
        message="Ada produk apa saja?",
        store=store_instance,
        customer_phone="6281234567890",
    )
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from app.agent.errors import get_fallback
from app.agent.graph import compile_graph
from app.agent.prompts import SYSTEM_PROMPT
from app.models.commerce import Store

log = structlog.get_logger()


class AgentExecutor:
    """Facade that invokes the compiled LangGraph commerce agent.

    Each call to :meth:`run` creates a fresh thread so conversations stay
    isolated.
    """

    def __init__(self) -> None:
        self._graph: CompiledStateGraph = compile_graph()  # type: ignore[type-arg]

    async def run(
        self,
        message: str,
        store: Store | None,
        customer_phone: str,
        customer_name: str | None = None,
        is_merchant: bool = False,
    ) -> str:
        """Run the agent for a single user message and return the reply text.

        Parameters
        ----------
        message:
            The raw text message from the customer or merchant.
        store:
            A SQLAlchemy ``Store`` instance (already loaded with relationships).
        customer_phone:
            WhatsApp phone number of the customer.
        customer_name:
            Optional display name of the customer.
        is_merchant:
            ``True`` when the sender is the store owner.

        Returns
        -------
        str
            The agent's reply text in Indonesian.
        """
        if not message or not message.strip():
            return get_fallback("unknown", "empty_message")

        if store is None:
            return "Maaf, saya tidak menemukan toko yang dimaksud. Silakan pilih toko terlebih dahulu."

        thread_id = uuid.uuid4().hex
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        context: dict[str, Any] = {
            "store_id": str(store.id),
            "store_name": store.name,
            "customer_phone": customer_phone,
            "customer_name": customer_name or "",
            "is_merchant": is_merchant,
        }

        system_content = SYSTEM_PROMPT.format(store_name=store.name)
        if store.custom_prompt:
            system_content += f"\n\nInstruksi tambahan dari toko:\n{store.custom_prompt}"

        input_messages: dict[str, Any] = {
            "messages": [
                SystemMessage(content=system_content),
                HumanMessage(content=message.strip()),
            ],
            "intent": "unknown",
            "entities": {},
            "cart": [],
            "context": context,
            "error": "",
            "tool_result": {},
            "response_text": "",
        }

        try:
            result = await self._graph.ainvoke(input_messages, config)
            reply: str = str(result.get("response_text", ""))
            if not reply:
                # Fallback: pull the last AIMessage from messages
                for msg in reversed(result.get("messages", [])):
                    if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content.strip():
                        reply = msg.content
                        break
        except Exception as e:
            log.error("agent_executor_run_error", error=str(e), thread_id=thread_id)
            reply = str(get_fallback("unknown"))

        return reply

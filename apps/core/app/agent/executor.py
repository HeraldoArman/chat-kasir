"""High-level executor that wires a user message through the ReAct commerce agent.

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
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from app.agent.graph import compile_graph
from app.models.commerce import Store

log = structlog.get_logger()


class AgentExecutor:
    """Facade that invokes the compiled ReAct commerce agent.

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
        """Run the ReAct agent for a single user message and return the reply.

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
            return "Maaf kak, pesannya kosong. Ada yang bisa saya bantu?"

        if store is None:
            return "Maaf kak, saya tidak menemukan tokonya. Silakan pilih toko dulu ya."

        thread_id = uuid.uuid4().hex
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        context: dict[str, Any] = {
            "store_id": str(store.id),
            "store_name": store.name,
            "customer_phone": customer_phone,
            "customer_name": customer_name or "",
            "is_merchant": is_merchant,
        }

        input_state: dict[str, Any] = {
            "messages": [HumanMessage(content=message.strip())],
            "context": context,
        }

        # Include custom prompt if set
        if store.custom_prompt:
            input_state["custom_prompt"] = store.custom_prompt

        try:
            result = await self._graph.ainvoke(input_state, config)
            reply = _extract_reply(result)
        except Exception as e:
            log.error("agent_executor_run_error", error=str(e), thread_id=thread_id)
            reply = "Maaf kak, ada gangguan sistem. Coba ulangi lagi ya."

        return reply


def _extract_reply(result: dict[str, Any]) -> str:
    """Pull the last AI message content from the graph output."""
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
            content = msg.content
            if isinstance(content, str) and content.strip():
                return content
            if isinstance(content, list):
                texts = [p.get("text", "") for p in content if isinstance(p, dict)]
                joined = " ".join(texts).strip()
                if joined:
                    return joined
    return ""

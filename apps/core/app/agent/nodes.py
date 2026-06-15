"""ReAct agent nodes for the commerce agent.

The agent uses tool-calling LLM (ReAct pattern) instead of a rigid
classify → extract → execute → respond pipeline.
"""

from __future__ import annotations

import json
from typing import Any, Literal

import structlog
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agent.prompts import CONTEXT_INSTRUCTIONS, SYSTEM_PROMPT
from app.agent.state import AgentState
from app.agent.tools import ALL_TOOLS
from app.core.config import get_config

log = structlog.get_logger()


# Tools that only the store owner may call.
_MERCHANT_ONLY_TOOLS: frozenset[str] = frozenset({
    "get_merchant_analytics",
    "verify_order_payment",
    "get_low_stock_products",
    "get_daily_summary",
    "update_product_stock",
    "create_product",
    "get_all_orders",
    "get_store_stats",
    "cancel_order",
    "update_product",
    "get_revenue_report",
    "forward_to_customer",
})

# Tools that need a customer_phone injected from the agent context.
_TOOLS_NEEDING_CUSTOMER_PHONE: frozenset[str] = frozenset({
    "create_order",
    "confirm_payment_notify_merchant",
    "get_order_status",
    "add_to_cart",
    "get_cart",
    "update_cart_item",
    "remove_from_cart",
    "checkout_cart",
    "recommend_products",
    "upsell_product",
    "cross_sell_product",
    "submit_complaint",
    "submit_refund_request",
    "get_customer_order_history",
    "forward_to_merchant",
})


def _get_llm() -> ChatOpenAI:
    """Create a ChatOpenAI instance from app config."""
    config = get_config()
    return ChatOpenAI(
        model=config.llm.model,
        temperature=config.llm.temperature,
        timeout=config.llm.timeout,
        max_tokens=config.llm.max_tokens,
        base_url=config.llm.base_url,
    )


# ---------------------------------------------------------------------------
# Node: call_agent
# ---------------------------------------------------------------------------


async def call_agent(state: AgentState) -> dict[str, Any]:
    """LLM node with tool bindings — the agent thinks and decides.

    The LLM can either respond directly (normal conversation) or invoke one
    or more tools in parallel.  The ``execute_tools`` node handles actual
    tool execution and context injection.
    """
    ctx = state.get("context", {})
    store_name = ctx.get("store_name", "")

    try:
        llm = _get_llm().bind_tools(ALL_TOOLS)

        system_content = SYSTEM_PROMPT.format(store_name=store_name)
        context_info = CONTEXT_INSTRUCTIONS.format(
            store_name=store_name,
            store_id=ctx.get("store_id", ""),
            customer_phone=ctx.get("customer_phone", ""),
            customer_name=ctx.get("customer_name", ""),
            is_merchant=ctx.get("is_merchant", False),
        )

        messages: list[Any] = [
            SystemMessage(content=system_content + "\n\n" + context_info),
            *state.get("messages", []),
        ]

        response = await llm.ainvoke(messages)
    except Exception as e:
        log.error("agent_call_llm_error", error=str(e))
        response = AIMessage(
            content="Maaf kak, saya lagi error nih. Coba ulangi lagi ya atau hubungi tokonya langsung."
        )

    return {"messages": [response]}


# ---------------------------------------------------------------------------
# Node: execute_tools
# ---------------------------------------------------------------------------


async def execute_tools(state: AgentState) -> dict[str, Any]:
    """Execute tool calls from the LLM, injecting context and enforcing guards.

    For each tool call the LLM made:
    1. Merchant-only check — reject if the sender isn't the store owner.
    2. Inject *store_id* (and *customer_phone* where needed) from agent
       context so the LLM doesn't have to manage these.
    3. Run the actual tool and wrap the result in a ``ToolMessage``.
    """
    last = state["messages"][-1] if state.get("messages") else None
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {"messages": []}

    ctx = state.get("context", {})
    results: list[ToolMessage] = []

    for tool_call in last.tool_calls:
        tool_name: str = tool_call["name"]
        tool_args: dict[str, Any] = dict(tool_call.get("args", {}))

        # ---- Merchant-only guard ----
        if tool_name in _MERCHANT_ONLY_TOOLS and not ctx.get("is_merchant"):
            results.append(
                ToolMessage(
                    content=json.dumps(
                        {
                            "success": False,
                            "message": "Maaf, fitur ini hanya tersedia untuk pemilik toko.",
                        },
                        ensure_ascii=False,
                    ),
                    tool_call_id=tool_call["id"],
                )
            )
            continue

        # ---- Inject context params ----
        tool_args["store_id"] = ctx.get("store_id", "")
        if tool_name in _TOOLS_NEEDING_CUSTOMER_PHONE:
            tool_args["customer_phone"] = ctx.get("customer_phone", "")
        if tool_name == "verify_order_payment":
            tool_args["merchant_phone"] = ctx.get("customer_phone", "")

        # ---- Dispatch ----
        tool_fn = next((t for t in ALL_TOOLS if t.name == tool_name), None)
        if tool_fn is None:
            results.append(
                ToolMessage(
                    content=json.dumps(
                        {"success": False, "message": f"Tool {tool_name} tidak ditemukan."},
                        ensure_ascii=False,
                    ),
                    tool_call_id=tool_call["id"],
                )
            )
            continue

        try:
            result = await tool_fn.ainvoke(tool_args)
            content = json.dumps(result, ensure_ascii=False)
        except Exception as e:
            log.error("agent_tool_execution_error", tool=tool_name, error=str(e))
            content = json.dumps(
                {"success": False, "message": f"Gagal menjalankan {tool_name}: {e}"},
                ensure_ascii=False,
            )

        results.append(ToolMessage(content=content, tool_call_id=tool_call["id"]))

    return {"messages": results}


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Route back to tools if the LLM made tool calls, otherwise end."""
    last = state.get("messages", [])[-1] if state.get("messages") else None
    if last is not None and getattr(last, "tool_calls", None):
        return "tools"
    return "__end__"

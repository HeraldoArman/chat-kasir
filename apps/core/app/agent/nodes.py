"""Graph nodes for the commerce agent.

Each node is an async function that receives the current ``AgentState`` and
returns a partial-update dict.  LLM-backed nodes use ``ChatOpenAI`` with
retry/timeout safety.  Deterministic fallbacks are provided when the LLM call
fails.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agent.errors import get_fallback
from app.agent.prompts import (
    ENTITY_EXTRACTION_PROMPT,
    INTENT_CLASSIFICATION_PROMPT,
    RESPONSE_GENERATION_PROMPT,
    SYSTEM_PROMPT,
)
from app.agent.state import AgentState
from app.agent.tools import ALL_TOOLS
from app.core.config import get_config

log = structlog.get_logger()

VALID_INTENTS = [
    "product_discovery",
    "create_order",
    "payment_info",
    "payment_confirmation",
    "order_status",
    "faq",
    "merchant_analytics",
    "verify_payment",
    "greeting",
    "unknown",
]

# Intent → tool name mapping
INTENT_TOOL_MAP: dict[str, str] = {
    "product_discovery": "search_products",
    "create_order": "create_order",
    "payment_info": "get_payment_info",
    "payment_confirmation": "confirm_payment_notify_merchant",
    "order_status": "get_order_status",
    "faq": "answer_faq",
    "merchant_analytics": "get_merchant_analytics",
    "verify_payment": "verify_order_payment",
}


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


def _get_last_user_message(state: AgentState) -> str:
    """Extract the text of the last HumanMessage from state."""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            content = msg.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                # Multimodal content – concatenate text parts
                return " ".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
    return ""


# ---------------------------------------------------------------------------
# Node: classify_intent
# ---------------------------------------------------------------------------


async def classify_intent(state: AgentState) -> dict[str, Any]:
    """Classify the user message into one of the valid intents."""
    message = _get_last_user_message(state)
    if not message.strip():
        return {"intent": "unknown", "error": "empty_message"}

    # Fast deterministic check for greeting
    greeting_words = {"halo", "hai", "hi", "hello", "selamat", "assalam", "pagi", "siang", "sore", "malam"}
    first_word = message.strip().lower().split()[0] if message.strip() else ""
    if first_word in greeting_words and len(message.strip()) < 30:
        return {"intent": "greeting"}

    try:
        llm = _get_llm()
        prompt = INTENT_CLASSIFICATION_PROMPT.format(message=message[:500])
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        intent_text = response.content.strip().lower() if isinstance(response.content, str) else "unknown"

        # Normalise: take the first word only if extra text is returned
        intent = intent_text.split()[0] if intent_text else "unknown"

        if intent not in VALID_INTENTS:
            log.warning("agent_unrecognized_intent", raw=intent_text, fallback="unknown")
            intent = "unknown"
    except Exception as e:
        log.error("agent_classify_intent_llm_error", error=str(e))
        intent = "unknown"

    return {"intent": intent}


# ---------------------------------------------------------------------------
# Node: extract_entities
# ---------------------------------------------------------------------------


async def extract_entities(state: AgentState) -> dict[str, Any]:
    """Extract structured entities from the user message using LLM."""
    message = _get_last_user_message(state)
    if not message.strip():
        return {"entities": {}}

    try:
        llm = _get_llm()
        prompt = ENTITY_EXTRACTION_PROMPT.format(message=message[:1000])
        response = await llm.ainvoke([HumanMessage(content=prompt)])

        content = response.content if isinstance(response.content, str) else ""
        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        entities: dict[str, Any] = json.loads(content)
    except json.JSONDecodeError:
        log.warning("agent_entity_extraction_json_error")
        entities = {}
    except Exception as e:
        log.error("agent_entity_extraction_llm_error", error=str(e))
        entities = {}

    return {"entities": entities}


# ---------------------------------------------------------------------------
# Node: route_by_intent
# ---------------------------------------------------------------------------


def route_by_intent(state: AgentState) -> Literal["extract_entities", "error_handler", "generate_response"]:
    """Route based on classified intent.

    - ``greeting`` → ``generate_response`` (no tool needed)
    - ``unknown`` → ``error_handler``
    - everything else → ``extract_entities`` then ``execute_tool``
    """
    intent = state.get("intent", "unknown")

    if intent == "greeting":
        return "generate_response"
    if intent == "unknown":
        return "error_handler"
    return "extract_entities"


# ---------------------------------------------------------------------------
# Node: execute_tool
# ---------------------------------------------------------------------------


async def execute_tool(state: AgentState) -> dict[str, Any]:
    """Execute the tool corresponding to the classified intent."""
    intent = state.get("intent", "unknown")
    tool_name = INTENT_TOOL_MAP.get(intent)
    if tool_name is None:
        return {"tool_result": {"success": False, "message": "Tidak ada tool untuk intent ini."}}

    tool_fn = next((t for t in ALL_TOOLS if t.name == tool_name), None)
    if tool_fn is None:
        return {"tool_result": {"success": False, "message": f"Tool {tool_name} tidak ditemukan."}}

    ctx = state.get("context", {})
    store_id = ctx.get("store_id", "")
    entities = state.get("entities", {})

    # Merchant-only guard
    merchant_only_intents = {"merchant_analytics", "verify_payment"}
    if intent in merchant_only_intents and not ctx.get("is_merchant", False):
        return {
            "tool_result": {
                "success": False,
                "message": "Maaf, fitur ini hanya tersedia untuk pemilik toko.",
                "edge_case": "customer_merchant_mismatch",
            }
        }

    try:
        if tool_name == "search_products":
            keywords = entities.get("keywords", []) or entities.get("product_names", [])
            result = await tool_fn.ainvoke({"store_id": store_id, "keywords": keywords})

        elif tool_name == "create_order":
            items = _build_order_items(state)
            result = await tool_fn.ainvoke({
                "store_id": store_id,
                "customer_phone": ctx.get("customer_phone", ""),
                "items": items,
                "note": entities.get("note"),
            })

        elif tool_name == "get_payment_info":
            result = await tool_fn.ainvoke({"store_id": store_id})

        elif tool_name == "confirm_payment_notify_merchant":
            result = await tool_fn.ainvoke({
                "store_id": store_id,
                "customer_phone": ctx.get("customer_phone", ""),
            })

        elif tool_name == "get_order_status":
            result = await tool_fn.ainvoke({
                "store_id": store_id,
                "customer_phone": ctx.get("customer_phone", ""),
            })

        elif tool_name == "verify_order_payment":
            order_id = _extract_order_id(state)
            result = await tool_fn.ainvoke({
                "store_id": store_id,
                "merchant_phone": ctx.get("customer_phone", ""),
                "order_id": order_id,
            })

        elif tool_name == "answer_faq":
            message = _get_last_user_message(state)
            result = await tool_fn.ainvoke({"store_id": store_id, "query": message[:500]})

        elif tool_name == "get_merchant_analytics":
            result = await tool_fn.ainvoke({"store_id": store_id})

        else:
            result = {"success": False, "message": f"Tool {tool_name} tidak didukung."}

    except Exception as e:
        log.error("agent_tool_execution_error", tool=tool_name, error=str(e))
        result = {"success": False, "message": f"Gagal menjalankan {tool_name}: {e}"}

    return {"tool_result": result}


def _build_order_items(state: AgentState) -> list[dict[str, Any]]:
    """Build order items from entities and cart."""
    items: list[dict[str, Any]] = []
    cart = state.get("cart", [])
    if cart:
        return [dict(item) for item in cart]

    entities = state.get("entities", {})
    product_names = entities.get("product_names", [])
    quantities = entities.get("quantities", [])

    for i, name in enumerate(product_names):
        qty = int(quantities[i]) if i < len(quantities) else 1
        if qty <= 0:
            qty = 1
        items.append({
            "product_id": "",
            "name": name,
            "quantity": qty,
            "unit_price": 0,
            "total_price": 0,
        })

    return items


def _extract_order_id(state: AgentState) -> str:
    """Extract an order UUID from entities or the raw user message."""
    entities = state.get("entities", {})
    order_id = entities.get("order_id", "")
    if isinstance(order_id, str) and order_id.strip():
        return order_id.strip()

    message = _get_last_user_message(state)
    match = re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", message)
    if match:
        return match.group(0)
    return ""


# ---------------------------------------------------------------------------
# Node: generate_response
# ---------------------------------------------------------------------------


async def generate_response(state: AgentState) -> dict[str, Any]:
    """Generate the final Indonesian response text.

    Uses LLM when tool_result is available; falls back to a deterministic
    greeting or error message otherwise.
    """
    intent = state.get("intent", "unknown")
    ctx = state.get("context", {})
    tool_result = state.get("tool_result")

    # Deterministic greeting path
    if intent == "greeting" and not tool_result:
        greeting = "Halo! 👋 Ada yang bisa saya bantu? "
        greeting += "Silakan tanyakan tentang produk, pemesanan, atau pembayaran."
        return {"response_text": greeting, "messages": [AIMessage(content=greeting)]}

    # Edge-case fallback from tool
    if tool_result and isinstance(tool_result, dict):
        edge_case = tool_result.get("edge_case")
        if edge_case:
            fallback = get_fallback(intent, edge_case)
            return {"response_text": fallback, "messages": [AIMessage(content=fallback)]}

    # LLM-powered response
    try:
        llm = _get_llm()
        store_name = ctx.get("store_name", "Toko")
        system_msg = SystemMessage(content=SYSTEM_PROMPT.format(store_name=store_name))

        prompt = RESPONSE_GENERATION_PROMPT.format(
            store_name=store_name,
            intent=intent,
            tool_result=json.dumps(tool_result, ensure_ascii=False) if tool_result else "{}",
            customer_context=json.dumps(
                {k: v for k, v in ctx.items() if k != "store_id"},
                ensure_ascii=False,
            ),
        )

        response = await llm.ainvoke([system_msg, HumanMessage(content=prompt)])
        text = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as e:
        log.error("agent_response_generation_error", error=str(e))
        text = get_fallback(intent)

    return {"response_text": text, "messages": [AIMessage(content=text)]}


# ---------------------------------------------------------------------------
# Node: error_handler
# ---------------------------------------------------------------------------


async def error_handler(state: AgentState) -> dict[str, Any]:
    """Handle errors and unknown intents with a deterministic fallback."""
    error = state.get("error", "")
    intent = state.get("intent", "unknown")

    if error == "empty_message":
        text = get_fallback("unknown", "empty_message")
    else:
        text = get_fallback(intent)

    return {"response_text": text, "messages": [AIMessage(content=text)]}

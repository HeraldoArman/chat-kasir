"""Typed state schema for the commerce agent graph."""

from __future__ import annotations

import operator
from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class CartItem(TypedDict):
    product_id: str
    name: str
    quantity: int
    unit_price: int
    total_price: int


class AgentContext(TypedDict, total=False):
    store_id: str
    store_name: str
    customer_phone: str
    customer_name: str
    is_merchant: bool


class AgentState(TypedDict, total=False):
    """State flowing through the commerce agent graph.

    ``messages`` uses ``operator.add`` so each node appends rather than
    overwriting.
    """

    messages: Annotated[list[BaseMessage], operator.add]
    intent: str
    entities: dict[str, Any]
    cart: list[CartItem]
    context: AgentContext
    error: str
    tool_result: dict[str, Any]
    response_text: str

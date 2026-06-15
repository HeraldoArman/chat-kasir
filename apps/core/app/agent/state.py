"""Typed state schema for the commerce agent graph.

The ReAct agent uses a minimal state: a message list (appended by each
node) and a context dict for store/merchant info.
"""

from __future__ import annotations

import operator
from typing import Annotated

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentContext(TypedDict, total=False):
    store_id: str
    store_name: str
    customer_phone: str
    customer_name: str
    is_merchant: bool


class AgentState(TypedDict, total=False):
    """State flowing through the ReAct agent graph.

    ``messages`` uses ``operator.add`` so each node appends rather than
    overwriting.
    """

    messages: Annotated[list[BaseMessage], operator.add]
    context: AgentContext

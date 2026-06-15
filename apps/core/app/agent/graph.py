"""Build and compile the commerce agent StateGraph.

Edges:  START → classify_intent → route_by_intent
          route_by_intent → extract_entities | error_handler | generate_response
          extract_entities → execute_tool → generate_response
          error_handler → END
          generate_response → END
"""

from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes import (
    classify_intent,
    error_handler,
    execute_tool,
    extract_entities,
    generate_response,
    route_by_intent,
)
from app.agent.state import AgentState


def build_graph() -> StateGraph:  # type: ignore[type-arg]
    """Return an un-compiled ``StateGraph`` for the commerce agent."""
    builder: StateGraph = StateGraph(AgentState)  # type: ignore[type-arg]

    # Register nodes
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("extract_entities", extract_entities)
    builder.add_node("execute_tool", execute_tool)
    builder.add_node("generate_response", generate_response)
    builder.add_node("error_handler", error_handler)

    # Entry
    builder.add_edge(START, "classify_intent")

    # Conditional routing after classification
    builder.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "extract_entities": "extract_entities",
            "error_handler": "error_handler",
            "generate_response": "generate_response",
        },
    )

    # extract → execute → generate → END
    builder.add_edge("extract_entities", "execute_tool")
    builder.add_edge("execute_tool", "generate_response")
    builder.add_edge("generate_response", END)

    # error → END
    builder.add_edge("error_handler", END)

    return builder


def compile_graph() -> CompiledStateGraph:  # type: ignore[type-arg]
    """Compile the commerce agent graph with an in-memory checkpointer.

    Returns a compiled graph ready for ``.invoke()`` / ``.stream()``.
    """
    builder = build_graph()
    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)

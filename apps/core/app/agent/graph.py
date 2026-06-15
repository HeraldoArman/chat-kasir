"""Build and compile the ReAct commerce agent state graph.

Edges:  START → call_agent
          call_agent → should_continue
            ┣━ tools → call_agent (loop)
            ┗━ END
"""

from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes import call_agent, execute_tools, should_continue
from app.agent.state import AgentState


def build_graph() -> StateGraph:  # type: ignore[type-arg]
    """Return an un-compiled ``StateGraph`` for the ReAct commerce agent."""
    builder: StateGraph = StateGraph(AgentState)  # type: ignore[type-arg]

    builder.add_node("agent", call_agent)
    builder.add_node("tools", execute_tools)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    builder.add_edge("tools", "agent")

    return builder


def compile_graph() -> CompiledStateGraph:  # type: ignore[type-arg]
    """Compile the agent graph with an in-memory checkpointer."""
    builder = build_graph()
    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)

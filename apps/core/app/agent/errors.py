"""Custom errors for the ReAct commerce agent.

Intent-based fallbacks are no longer needed — the LLM handles response
generation naturally through its system prompt and tool-calling loop.
"""

from __future__ import annotations


class AgentError(Exception):
    """Base error for agent-level failures."""

    def __init__(self, message: str, detail: str | None = None) -> None:
        self.detail = detail
        super().__init__(message)


class LLMUnavailableError(AgentError):
    """Raised when the LLM call fails after retries."""


class ToolExecutionError(AgentError):
    """Raised when a tool call returns an unexpected error."""

"""Shared helpers for direct and optional LangChain-compatible tools."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def make_langchain_tool(name: str, description: str, func: Callable[..., dict[str, Any]]) -> Any | None:
    """Create a LangChain StructuredTool when LangChain is installed.

    Direct Python tool classes remain the primary interface for the project. This
    helper returns `None` when LangChain tool abstractions are not importable.
    """
    try:
        from langchain_core.tools import StructuredTool
    except Exception:
        return None

    return StructuredTool.from_function(func=func, name=name, description=description)


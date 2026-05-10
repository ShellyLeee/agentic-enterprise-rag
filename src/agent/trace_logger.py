"""Trace persistence for explicit Agentic RAG runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AgentTraceLogger:
    """Persist structured agent traces as JSON."""

    def save(self, trace: dict[str, Any], output_path: str | Path) -> Path:
        """Save a trace to disk and return the path."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
        return path


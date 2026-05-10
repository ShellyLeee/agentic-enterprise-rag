"""Trace logging for agent runs.

TODO:
- Persist AgentTrace records as JSONL.
- Attach model usage, retrieval candidates, rerank scores, policy decisions, and errors.
"""

import json
from pathlib import Path

from src.schemas import AgentTrace


class TraceLogger:
    """Writes agent traces to local artifacts."""

    def __init__(self, trace_dir: str | Path) -> None:
        self.trace_dir = Path(trace_dir)

    def write(self, trace: AgentTrace) -> Path:
        """Persist a trace as JSON.

        This lightweight implementation is useful during scaffolding and can be
        replaced by JSONL, OpenTelemetry, or LangSmith integration later.
        """
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        path = self.trace_dir / f"{trace.trace_id}.json"
        path.write_text(json.dumps(trace.model_dump(mode="json"), indent=2), encoding="utf-8")
        return path


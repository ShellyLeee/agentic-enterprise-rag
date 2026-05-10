"""Offline evaluation runner.

TODO:
- Load golden questions from JSONL.
- Run the agent on each question.
- Compute answer, citation, retrieval, latency, and cost metrics.
"""


class EvaluationRunner:
    """Runs repeatable evaluations against a golden set."""

    def run(self) -> dict:
        """Run evaluation and return aggregate metrics."""
        raise NotImplementedError


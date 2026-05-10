"""CLI placeholder for online agentic question answering.

TODO:
- Load the configured retriever, reranker, agent policy, and answer generator.
- Run the evidence-aware agent and emit an AgentTrace.
"""

import typer


app = typer.Typer(help="Ask the agentic enterprise RAG system a question.")


@app.command()
def main(question: str, config: str = "configs/default.yaml") -> None:
    """Ask a question."""
    raise NotImplementedError(f"Question answering is not implemented yet: {question!r}. Config: {config}")


if __name__ == "__main__":
    app()


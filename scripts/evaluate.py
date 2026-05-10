"""CLI placeholder for offline evaluation.

TODO:
- Load a golden set from `data/eval`.
- Run the agent over each row.
- Write metrics and traces to `results`.
"""

import typer


app = typer.Typer(help="Evaluate the agentic RAG system.")


@app.command()
def main(config: str = "configs/default.yaml") -> None:
    """Run evaluation."""
    raise NotImplementedError(f"Evaluation is not implemented yet. Config: {config}")


if __name__ == "__main__":
    app()


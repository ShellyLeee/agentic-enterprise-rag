"""CLI placeholder for offline document ingestion.

TODO:
- Load `configs/default.yaml`.
- Parse raw documents from `data/raw_docs`.
- Write normalized documents to `data/processed`.
"""

import typer


app = typer.Typer(help="Ingest and normalize enterprise documents.")


@app.command()
def main(config: str = "configs/default.yaml") -> None:
    """Run the ingestion stage."""
    raise NotImplementedError(f"Ingestion is not implemented yet. Config: {config}")


if __name__ == "__main__":
    app()


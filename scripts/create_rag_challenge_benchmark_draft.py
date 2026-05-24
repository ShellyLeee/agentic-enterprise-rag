#!/usr/bin/env python
"""Create a small manual-review benchmark draft from RAG-Challenge chunks.

This script is intentionally deterministic and conservative. It does not call
external APIs. Each non-OOD item is backed by one or more real chunks selected
with explicit phrase matches.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_CHUNKS_PATH = Path("data/processed/rag_challenge_test_index/chunks.jsonl")
DEFAULT_OUTPUT_PATH = Path("data/eval/rag_challenge_test_set_draft_10.jsonl")
DEFAULT_REVIEW_PATH = Path("data/eval/rag_challenge_test_set_draft_10_review.md")
OOD_ANSWER = "Not sure based on the provided documents."


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_chunks(path: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            chunk = json.loads(line)
            chunk["_line_number"] = line_number
            chunks.append(chunk)
    if not chunks:
        raise ValueError(f"No chunks found in {path}")
    return chunks


def chunk_doc_name(chunk: dict[str, Any]) -> str:
    metadata = chunk.get("metadata") or {}
    return (
        chunk.get("doc_name")
        or chunk.get("source_doc")
        or metadata.get("file_name")
        or Path(str(metadata.get("source_path", ""))).name
        or str(chunk.get("document_id", "unknown"))
    )


def chunk_page_num(chunk: dict[str, Any]) -> int | None:
    metadata = chunk.get("metadata") or {}
    return (
        chunk.get("page_num")
        or chunk.get("page")
        or chunk.get("page_number")
        or metadata.get("page_num")
        or metadata.get("page")
        or metadata.get("page_number")
    )


def evidence_from_chunk(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "doc_name": chunk_doc_name(chunk),
        "page_num": chunk_page_num(chunk),
        "chunk_id": chunk.get("chunk_id") or (chunk.get("metadata") or {}).get("chunk_id"),
        "evidence_text": chunk.get("text", ""),
    }


def find_chunk(
    chunks: list[dict[str, Any]],
    *,
    file_name: str,
    phrases: list[str],
) -> dict[str, Any]:
    lowered_phrases = [phrase.lower() for phrase in phrases]
    for chunk in chunks:
        if chunk_doc_name(chunk) != file_name:
            continue
        text = normalize_ws(str(chunk.get("text", ""))).lower()
        if all(phrase in text for phrase in lowered_phrases):
            return chunk
    raise ValueError(f"No chunk found for {file_name} with phrases: {phrases}")


def gold_doc_id(source_doc: str) -> str:
    return source_doc.removesuffix(".pdf")


def build_items(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    holley = "194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf"
    tradition = "2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf"
    yellow = "9d7a72445aba6860402c3acce75af02dc045f74d.pdf"
    crossfirst = "e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf"

    holley_brand = find_chunk(
        chunks,
        file_name=holley,
        phrases=["portfolio consists of over 70 brands", "Holley EFI", "represented 14%"],
    )
    holley_employees = find_chunk(
        chunks,
        file_name=holley,
        phrases=["1,622 full-time employees", "100 temporary employees"],
    )
    holley_dividends = find_chunk(
        chunks,
        file_name=holley,
        phrases=["do not intend to pay cash dividends", "foreseeable future"],
    )
    crossfirst_branches = find_chunk(
        chunks,
        file_name=crossfirst,
        phrases=["branches are strategically located", "Kansas", "New Mexico"],
    )
    crossfirst_acquisition = find_chunk(
        chunks,
        file_name=crossfirst,
        phrases=["Farmers & Stockmens Bank", "$389 million of loans", "$570 million of deposits"],
    )
    crossfirst_highlights = find_chunk(
        chunks,
        file_name=crossfirst,
        phrases=["$ 6.6", "TOTAL ASSETS", "LOANS GREW"],
    )
    tradition_margin = find_chunk(
        chunks,
        file_name=tradition,
        phrases=["operating margin of 12.7%", "10.5% respectively"],
    )
    yellow_repurchase = find_chunk(
        chunks,
        file_name=yellow,
        phrases=["distributed $100.0 million", "share repurchase"],
    )

    items = [
        {
            "id": "q001",
            "question": "Which brand did Holley identify as its largest brand in 2022?",
            "answer": "Holley EFI",
            "type": "fact_qa",
            "source_doc": holley,
            "evidence": [evidence_from_chunk(holley_brand)],
            "difficulty": "easy",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "Included as a direct fact question; the chunk states Holley EFI was the largest brand and represented 14% of 2022 sales.",
            "gold_doc_ids": [gold_doc_id(holley)],
            "gold_evidence_keywords": ["Holley EFI", "largest brand", "14%"],
        },
        {
            "id": "q002",
            "question": "In which states are CrossFirst Bank's branches strategically located?",
            "answer": "Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico.",
            "type": "fact_qa",
            "source_doc": crossfirst,
            "evidence": [evidence_from_chunk(crossfirst_branches)],
            "difficulty": "easy",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "Included as a direct fact question with an explicit state list in one chunk.",
            "gold_doc_ids": [gold_doc_id(crossfirst)],
            "gold_evidence_keywords": ["branches", "Kansas", "Missouri", "Oklahoma", "Texas", "Arizona", "Colorado", "New Mexico"],
        },
        {
            "id": "q003",
            "question": "As of December 31, 2022, how many full-time and temporary employees did Holley employ?",
            "answer": "1,622 full-time employees and 100 temporary employees.",
            "type": "numerical",
            "source_doc": holley,
            "evidence": [evidence_from_chunk(holley_employees)],
            "difficulty": "easy",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "Numerical sample with explicit headcount figures; no unit conversion is needed.",
            "gold_doc_ids": [gold_doc_id(holley)],
            "gold_evidence_keywords": ["1,622 full-time employees", "100 temporary employees"],
        },
        {
            "id": "q004",
            "question": "What were Tradition's underlying operating profitability margins for 2022 and 2021?",
            "answer": "12.7% in 2022 and 10.5% in 2021.",
            "type": "numerical",
            "source_doc": tradition,
            "evidence": [evidence_from_chunk(tradition_margin)],
            "difficulty": "medium",
            "requires_rewrite": True,
            "requires_multi_hop": False,
            "notes": "Numerical percentage sample; the question uses a more colloquial wording while the evidence uses 'operating margin'. No unit conversion is needed.",
            "gold_doc_ids": [gold_doc_id(tradition)],
            "gold_evidence_keywords": ["operating margin", "12.7%", "10.5%"],
        },
        {
            "id": "q005",
            "question": "What evidence shows Holley was both a broad brand portfolio company and a sizable employer at the end of 2022?",
            "answer": "Holley's portfolio had over 70 brands across 30 product categories, and it employed 1,622 full-time employees plus 100 temporary employees as of December 31, 2022.",
            "type": "multi_hop",
            "source_doc": holley,
            "evidence": [evidence_from_chunk(holley_brand), evidence_from_chunk(holley_employees)],
            "difficulty": "medium",
            "requires_rewrite": True,
            "requires_multi_hop": True,
            "notes": "Multi-hop item across two Holley chunks/pages: brand portfolio scale and employee headcount. The question wording abstracts from exact document terms.",
            "gold_doc_ids": [gold_doc_id(holley)],
            "gold_evidence_keywords": ["over 70 brands", "30 product categories", "1,622 full-time employees", "100 temporary employees"],
        },
        {
            "id": "q006",
            "question": "Which acquisition expanded CrossFirst in 2022, and what adjusted diluted EPS and adjusted ROE did CrossFirst report for that year?",
            "answer": "CrossFirst completed the acquisition of Farmers & Stockmens Bank ('Central'); for the year it delivered $1.37 in adjusted diluted earnings per share and adjusted ROE improved to 11.11% in 2022.",
            "type": "multi_hop",
            "source_doc": crossfirst,
            "evidence": [evidence_from_chunk(crossfirst_acquisition), evidence_from_chunk(crossfirst_highlights)],
            "difficulty": "hard",
            "requires_rewrite": True,
            "requires_multi_hop": True,
            "notes": "Multi-hop item using two CrossFirst chunks: one names the acquisition, while another supports the adjusted EPS and adjusted ROE figures.",
            "gold_doc_ids": [gold_doc_id(crossfirst)],
            "gold_evidence_keywords": ["Farmers & Stockmens Bank", "Central", "$1.37", "adjusted diluted earnings per share", "11.11%"],
        },
        {
            "id": "q007",
            "question": "Does Holley say it plans to pay cash dividends for the foreseeable future?",
            "answer": "false",
            "type": "boolean",
            "source_doc": holley,
            "evidence": [evidence_from_chunk(holley_dividends)],
            "difficulty": "easy",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "Boolean sample where the evidence directly states Holley does not intend to pay cash dividends for the foreseeable future.",
            "gold_doc_ids": [gold_doc_id(holley)],
            "gold_evidence_keywords": ["do not intend", "cash dividends", "foreseeable future"],
        },
        {
            "id": "q008",
            "question": "Did Yellow Pages distribute $100.0 million to shareholders through a share repurchase in 2022?",
            "answer": "true",
            "type": "boolean",
            "source_doc": yellow,
            "evidence": [evidence_from_chunk(yellow_repurchase)],
            "difficulty": "easy",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "Boolean sample supported by a direct statement about the 2022 statutory plan of arrangement and share repurchase.",
            "gold_doc_ids": [gold_doc_id(yellow)],
            "gold_evidence_keywords": ["distributed $100.0 million", "share repurchase", "2022"],
        },
        {
            "id": "q009",
            "question": "What was Apple's research and development expense in fiscal 2022?",
            "answer": OOD_ANSWER,
            "type": "ood",
            "source_doc": "N/A - not supported by current 5 PDF set",
            "evidence": [],
            "difficulty": "easy",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "OOD because the current PDF set contains Holley, Tradition, Yellow Pages, Mercia, and CrossFirst reports, not Apple financial statements.",
            "gold_doc_ids": [],
            "gold_evidence_keywords": [],
        },
        {
            "id": "q010",
            "question": "What greenhouse gas emissions reduction target did Tesla set for 2030 in these documents?",
            "answer": OOD_ANSWER,
            "type": "ood",
            "source_doc": "N/A - not supported by current 5 PDF set",
            "evidence": [],
            "difficulty": "medium",
            "requires_rewrite": False,
            "requires_multi_hop": False,
            "notes": "OOD because none of the current five PDFs is a Tesla report or provides sufficient evidence for Tesla's 2030 emissions targets.",
            "gold_doc_ids": [],
            "gold_evidence_keywords": [],
        },
    ]
    return items


def write_jsonl(items: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for item in items:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_review(items: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_type: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_type.setdefault(item["type"], []).append(item)

    lines = ["# RAG-Challenge Test Set Draft Review", ""]
    for item_type in ["fact_qa", "numerical", "multi_hop", "boolean", "ood"]:
        lines.append(f"## {item_type}")
        lines.append("")
        for item in by_type.get(item_type, []):
            lines.extend(
                [
                    f"### {item['id']}",
                    "",
                    f"- type: {item['type']}",
                    f"- question: {item['question']}",
                    f"- answer: {item['answer']}",
                    f"- source_doc: {item['source_doc']}",
                    f"- difficulty: {item['difficulty']}",
                    f"- requires_rewrite: {item['requires_rewrite']}",
                    f"- requires_multi_hop: {item['requires_multi_hop']}",
                    f"- notes: {item['notes']}",
                    "- evidence excerpt:",
                ]
            )
            if item["evidence"]:
                for evidence in item["evidence"]:
                    excerpt = normalize_ws(evidence["evidence_text"])[:700]
                    lines.append(
                        f"  - {evidence['doc_name']} p.{evidence['page_num']} "
                        f"chunk `{evidence['chunk_id']}`: {excerpt}"
                    )
            else:
                lines.append("  - None; this is an OOD item.")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a 10-example RAG-Challenge benchmark draft.")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args()

    chunks = load_chunks(args.chunks)
    docs = Counter(chunk_doc_name(chunk) for chunk in chunks)
    items = build_items(chunks)
    write_jsonl(items, args.output)
    write_review(items, args.review)

    print(f"chunks_path={args.chunks}")
    print(f"chunk_count={len(chunks)}")
    print("source_docs:")
    for doc_name, count in sorted(docs.items()):
        print(f"  {doc_name}: {count}")
    print(f"output={args.output}")
    print(f"review={args.review}")
    print("type_distribution:")
    for item_type, count in sorted(Counter(item['type'] for item in items).items()):
        print(f"  {item_type}: {count}")


if __name__ == "__main__":
    main()

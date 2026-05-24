#!/usr/bin/env python
"""Create the final 100-example custom PDF RAG benchmark.

The benchmark is generated from explicit phrase matches against local
RAG-Challenge chunks. Non-OOD answers are grounded in real chunk text; OOD
answers use a fixed abstention string.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.create_rag_challenge_benchmark_50 import (
    DOCS,
    EVIDENCE_QUERIES,
    DEFAULT_CHUNKS_PATH,
    OOD_ANSWER,
    chunk_doc_name,
    evidence_from_chunk,
    find_chunk,
    item_specs as first_50_specs,
    load_chunks,
    normalize_ws,
)


DEFAULT_OUTPUT_PATH = Path("data/eval/rag_challenge_test_set.jsonl")
DEFAULT_REVIEW_PATH = Path("data/eval/rag_challenge_test_set_review.md")

EXTRA_EVIDENCE_QUERIES = {
    "h_gross_profit": ("holley", ["Gross profit", "$253.7 million", "36.8%"]),
    "h_cogs": ("holley", ["Cost of goods sold", "$434.8 million", "$406.0 million"]),
    "h_acq_cash": ("holley", ["cash paid for the three acquisitions", "$14,863", "$9,618"]),
    "h_dividend_history": ("holley", ["never declared or paid any cash dividends", "foreseeable future"]),
    "h_bowling": ("holley", ["approximately 48%", "Bowling Green"]),
    "t_revenue": ("tradition", ["adjusted consolidated revenue", "CHF 1,028.6m", "CHF 950.8m"]),
    "t_idb_revenue": ("tradition", ["Adjusted revenue from interdealer broking business", "CHF 994.7m", "CHF 33.9m"]),
    "t_bonus_distribution": ("tradition", ["CHF 40,781,000", "one bonus share for every 100 shares"]),
    "t_share_info": ("tradition", ["one treasury share for every 100 shares held"]),
    "y_arrangement_shares": ("yellow", ["7,949,125 common shares", "purchase price of $12.58"]),
    "y_options": ("yellow", ["nil stock options exercisable", "2,132,132"]),
    "m_fvm_cash_return": ("mercia", ["£11.4million fair value movements", "c.£87million of cash returned"]),
    "m_nav_cash": ("mercia", ["45.6p", "Net assets per share", "£61.3m", "Cash"]),
    "m_final_dividend": ("mercia", ["0.5 pence per share", "0.8 pence per share", "0.4 pence per share"]),
    "m_faradion_return": ("mercia", ["4.4x return", "c.72% internal rate of return"]),
    "m_invincibles": ("mercia", ["Invincibles Studio", "40% year-on-year", "Avid Games"]),
    "m_ndreams": ("mercia", ["nDreams", "33.2%", "$35million"]),
    "c_balance_metrics": ("crossfirst", ["Total assets were $6.6 billion", "$5.4 billion in loans", "$687 million in securities"]),
    "c_nim": ("crossfirst", ["Net Interest Margin", "3.32%", "3.50%"]),
    "c_nim_detail": ("crossfirst", ["net interest margin", "increased to 3.50%", "3.17%"]),
    "y_pension_detail": ("yellow", ["net cash outlay of $96.1 million", "advanced $24.0 million to the Defined Benefit Pension Plan"]),
}


def extra_specs() -> list[dict[str, Any]]:
    ood_source = "N/A - not supported by current 5 PDF set"
    return [
        # fact_qa: q051-q060
        {"id": "q051", "type": "fact_qa", "question": "What year was Holley founded?", "answer": "1903.", "evidence_keys": ["h_founded"], "difficulty": "easy", "notes": "Direct company-history fact from Holley's business overview."},
        {"id": "q052", "type": "fact_qa", "question": "About how many specialist desks did Tradition say its brokers are organized into?", "answer": "Around 300 different desks.", "evidence_keys": ["t_desks"], "difficulty": "easy", "requires_rewrite": True, "notes": "Uses 'specialist desks' wording while evidence says each desk is a centre of expertise."},
        {"id": "q053", "type": "fact_qa", "question": "Which product-service categories does Yellow Pages say the CEO reviews revenues by?", "answer": "Print and Digital.", "evidence_keys": ["y_ceo_metric"], "difficulty": "medium", "requires_rewrite": True, "notes": "Question asks for revenue categories; evidence says the CEO reviews revenues by Print and Digital."},
        {"id": "q054", "type": "fact_qa", "question": "What did Mercia say about the geographic scope of its investing?", "answer": "Mercia said it invests exclusively in the UK.", "evidence_keys": ["m_uk"], "difficulty": "easy", "notes": "Direct Mercia fact about investment geography."},
        {"id": "q055", "type": "fact_qa", "question": "What did CrossFirst say its bank offers to commercial and consumer clients?", "answer": "A broad offering of deposit and lending products.", "evidence_keys": ["c_branches"], "difficulty": "easy", "notes": "Direct CrossFirst business-model fact."},
        {"id": "q056", "type": "fact_qa", "question": "Which Mercia portfolio company benefited from a $35 million investment from Aonic?", "answer": "nDreams.", "evidence_keys": ["m_ndreams"], "difficulty": "medium", "requires_rewrite": True, "notes": "Question uses portfolio-company wording; evidence names nDreams and Aonic."},
        {"id": "q057", "type": "fact_qa", "question": "What was the name of the bank CrossFirst completed acquiring in 2022?", "answer": "Farmers & Stockmens Bank ('Central').", "evidence_keys": ["c_acquisition"], "difficulty": "easy", "notes": "Direct acquisition-name fact."},
        {"id": "q058", "type": "fact_qa", "question": "What two revenue streams does Yellow Pages say its revenues consist of?", "answer": "Digital and print revenues.", "evidence_keys": ["y_declines"], "difficulty": "medium", "requires_rewrite": True, "notes": "Uses revenue-stream wording; evidence discusses digital revenues and print revenues."},
        {"id": "q059", "type": "fact_qa", "question": "What did Tradition say clients benefit from when placing orders?", "answer": "Anonymity that reduces the market impact of placing orders.", "evidence_keys": ["t_desks"], "difficulty": "medium", "notes": "Direct fact from Tradition's operating-model description."},
        {"id": "q060", "type": "fact_qa", "question": "Which Holley facilities were many full-time employees based around?", "answer": "The Bowling Green, KY headquarters, distribution center and manufacturing plants.", "evidence_keys": ["h_bowling"], "difficulty": "easy", "notes": "Direct Holley employee-location fact."},
        # numerical: q061-q070
        {"id": "q061", "type": "numerical", "question": "What were Holley's gross profit and gross margin for 2022?", "answer": "$253.7 million gross profit and 36.8% gross margin.", "evidence_keys": ["h_gross_profit"], "difficulty": "medium", "requires_rewrite": True, "notes": "Metric-specific numeric item; asks for gross profit and gross margin, not net sales."},
        {"id": "q062", "type": "numerical", "question": "What was Holley's cost of goods sold for 2022 and the 2021 comparison?", "answer": "$434.8 million in 2022 compared to $406.0 million in 2021.", "evidence_keys": ["h_cogs"], "difficulty": "medium", "notes": "Wrong-metric distractor for sales/profit; no unit conversion is needed."},
        {"id": "q063", "type": "numerical", "question": "What cash did Holley say it paid for the three 2022 acquisitions, net of cash acquired?", "answer": "$14,863, as stated in the acquisition note.", "evidence_keys": ["h_acq_cash"], "difficulty": "hard", "requires_rewrite": True, "notes": "Accounting-note numeric item with possible unit ambiguity; answer preserves the stated figure."},
        {"id": "q064", "type": "numerical", "question": "What adjusted consolidated revenue did Tradition report for 2022 and 2021?", "answer": "CHF 1,028.6m in 2022 compared with CHF 950.8m in 2021.", "evidence_keys": ["t_revenue"], "difficulty": "medium", "requires_rewrite": True, "notes": "Metric/year ambiguity: asks adjusted consolidated revenue, not profit."},
        {"id": "q065", "type": "numerical", "question": "What adjusted revenue did Tradition report for IDB and non-IDB activity?", "answer": "CHF 994.7m for IDB and CHF 33.9m for non-IDB.", "evidence_keys": ["t_idb_revenue"], "difficulty": "hard", "requires_rewrite": True, "notes": "Uses IDB/non-IDB aliases from the evidence; no currency conversion is needed."},
        {"id": "q066", "type": "numerical", "question": "What were Yellow Pages' 2022 total, digital, and print revenue decline rates?", "answer": "Total revenue declined 6.7%, digital revenue declined 5.6%, and print revenue declined 10.6%.", "evidence_keys": ["y_declines"], "difficulty": "hard", "requires_rewrite": True, "notes": "Metric ambiguity among total, digital, and print revenue decline rates."},
        {"id": "q067", "type": "numerical", "question": "How many common shares did Yellow Pages repurchase under the arrangement, and at what price per share?", "answer": "7,949,125 common shares at $12.58 per share.", "evidence_keys": ["y_arrangement_shares"], "difficulty": "medium", "notes": "Share-count and per-share-price numeric item."},
        {"id": "q068", "type": "numerical", "question": "What net assets per share and cash did Mercia report in its 2022 CFO highlights?", "answer": "45.6p net assets per share and £61.3m cash.", "evidence_keys": ["m_nav_cash"], "difficulty": "medium", "requires_rewrite": True, "notes": "Metric-specific Mercia numeric item; asks for per-share NAV and cash."},
        {"id": "q069", "type": "numerical", "question": "What return multiple and IRR did Mercia report for its Faradion direct holding?", "answer": "A 4.4x return and a c.72% internal rate of return.", "evidence_keys": ["m_faradion_return"], "difficulty": "medium", "requires_rewrite": True, "notes": "Uses return shorthand and IRR alias; no unit conversion is needed."},
        {"id": "q070", "type": "numerical", "question": "From 2019 to 2022, what did CrossFirst say its net interest margin improved from and to?", "answer": "From 3.32% in 2019 to 3.50% in 2022.", "evidence_keys": ["c_nim"], "difficulty": "medium", "requires_rewrite": True, "notes": "Year-specific metric question; asks NIM/FTE rather than revenue."},
        # multi_hop: q071-q080
        {"id": "q071", "type": "multi_hop", "question": "How do Holley's 2022 net sales and gross profit figures show different performance signals?", "answer": "Holley's 2022 net sales were $688.4 million versus $692.9 million in 2021, while gross profit decreased to $253.7 million and gross margin was 36.8%.", "evidence_keys": ["h_net_sales", "h_gross_profit"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Cross-chunk metric comparison designed to avoid confusing revenue with gross profit."},
        {"id": "q072", "type": "multi_hop", "question": "What did Tradition report for adjusted consolidated revenue and adjusted underlying operating profit?", "answer": "Tradition reported adjusted consolidated revenue of CHF 1,028.6m and adjusted underlying operating profit of CHF 130.3m.", "evidence_keys": ["t_revenue", "t_margin"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines revenue and profit metrics across chunks; useful for wrong-metric traps."},
        {"id": "q073", "type": "multi_hop", "question": "How did Yellow Pages combine revenue decline with margin improvement in 2022?", "answer": "Total revenues decreased 6.7% to $268.3 million, while the adjusted EBITDA margin increased to 36.0% from 35.5%.", "evidence_keys": ["y_revenues", "y_ebitda"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Requires combining revenue pressure with EBITDA-margin improvement, a partial-evidence trap."},
        {"id": "q074", "type": "multi_hop", "question": "What evidence shows Mercia had both realised cash from Faradion and fair-value movement from nDreams?", "answer": "Mercia received £19.4 million of cash proceeds from Faradion and nDreams added £6.7 million of fair value movement for Mercia's 33.2% direct holding stake.", "evidence_keys": ["m_faradion_sale", "m_ndreams"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Cross-chunk Mercia investment-performance synthesis."},
        {"id": "q075", "type": "multi_hop", "question": "What evidence shows CrossFirst improved both margin and credit-quality metrics?", "answer": "CrossFirst's net interest margin improved from 3.32% in 2019 to 3.50% in 2022, and its non-performing assets ratio declined from 0.97% at the end of 2019 to 0.20% at the end of 2022.", "evidence_keys": ["c_nim_detail", "c_revenue"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines NIM and NPA ratio from separate CrossFirst chunks; tests metric disambiguation."},
        {"id": "q076", "type": "multi_hop", "question": "Which companies did Holley acquire in 2022, and how much cash was paid for the three acquisitions?", "answer": "Holley acquired John's, SKC, and RaceQuip; cash paid for the three acquisitions, net of cash acquired, was $14,863.", "evidence_keys": ["h_acquisitions", "h_acq_cash"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines acquisition names and accounting-note amount across chunks."},
        {"id": "q077", "type": "multi_hop", "question": "What shareholder distributions did Tradition propose in both per-share and aggregate terms?", "answer": "Tradition proposed a cash dividend of CHF 5.50 per share, estimated at CHF 40,781,000, plus one bonus share for every 100 shares held.", "evidence_keys": ["t_dividend", "t_bonus_distribution"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Cross-page shareholder distribution question with per-share and aggregate figures."},
        {"id": "q078", "type": "multi_hop", "question": "What evidence shows Mercia had external fund awards and a strong cash position?", "answer": "The British Business Bank awarded £31.4 million to Mercia's equity and debt funds, and Mercia reported £61.3m of cash in its CFO highlights.", "evidence_keys": ["m_highlights", "m_nav_cash"], "difficulty": "medium", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines operational funding highlight with balance-sheet cash."},
        {"id": "q079", "type": "multi_hop", "question": "How did Yellow Pages' arrangement affect both shareholders and its pension plan?", "answer": "Yellow Pages distributed $100.0 million to shareholders by share repurchase and advanced $24.0 million of voluntary contributions to its Defined Benefit Pension Plan's wind-up deficit.", "evidence_keys": ["y_repurchase", "y_pension_detail"], "difficulty": "medium", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines shareholder and pension-plan consequences from separate arrangement chunks."},
        {"id": "q080", "type": "multi_hop", "question": "What evidence shows CrossFirst's growth involved both long-term branch expansion and the 2022 Central acquisition?", "answer": "CrossFirst opened its first branch in 2007 and grew through branches and acquisitions; in 2022 it completed the Farmers & Stockmens Bank ('Central') acquisition, adding $389 million of loans and $570 million of deposits.", "evidence_keys": ["c_first_branch", "c_acquisition"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines historical branch growth with 2022 acquisition evidence."},
        # boolean: q081-q090
        {"id": "q081", "type": "boolean", "question": "Had Holley ever declared or paid cash dividends on its capital stock?", "answer": "false", "evidence_keys": ["h_dividend_history"], "difficulty": "medium", "requires_rewrite": True, "notes": "Negation wording: evidence says Holley had never declared or paid cash dividends."},
        {"id": "q082", "type": "boolean", "question": "Did Holley's top seven brands generate 68% of its sales in 2022?", "answer": "true", "evidence_keys": ["h_brand"], "difficulty": "easy", "notes": "Boolean numeric check from Holley's brand portfolio chunk."},
        {"id": "q083", "type": "boolean", "question": "Did Yellow Pages' adjusted EBITDA margin decrease to 35.5% in 2022?", "answer": "false", "evidence_keys": ["y_ebitda"], "difficulty": "hard", "requires_rewrite": True, "notes": "Subtle wrong-year/wrong-direction trap: margin increased to 36.0%, compared to 35.5% last year."},
        {"id": "q084", "type": "boolean", "question": "Was Mercia's direct investment portfolio valued at £96.2 million as at 31 March 2022?", "answer": "false", "evidence_keys": ["m_direct_portfolio"], "difficulty": "hard", "requires_rewrite": True, "notes": "Wrong-year comparator trap: £96.2m was the 2021 comparator, while 2022 was £119.6m."},
        {"id": "q085", "type": "boolean", "question": "Did CrossFirst say its non-performing assets ratio declined to 0.20% by the end of 2022?", "answer": "true", "evidence_keys": ["c_revenue"], "difficulty": "medium", "notes": "Boolean credit-quality metric check."},
        {"id": "q086", "type": "boolean", "question": "Were Tradition's net exceptional costs lower in 2022 than in the previous year?", "answer": "false", "evidence_keys": ["t_exceptional"], "difficulty": "hard", "requires_rewrite": True, "notes": "Negation/wrong-direction trap: evidence says CHF 12.9m compared with CHF 5.8m in the previous year."},
        {"id": "q087", "type": "boolean", "question": "Did Yellow Pages' common share purchase warrants expire on December 20, 2022?", "answer": "true", "evidence_keys": ["y_warrants"], "difficulty": "easy", "notes": "Direct boolean date check."},
        {"id": "q088", "type": "boolean", "question": "Did Mercia report a 4.4x return for its Faradion direct holding?", "answer": "true", "evidence_keys": ["m_faradion_return"], "difficulty": "medium", "notes": "Boolean return-multiple check."},
        {"id": "q089", "type": "boolean", "question": "Were approximately 48% of Holley's full-time employees based primarily around Bowling Green, KY?", "answer": "true", "evidence_keys": ["h_bowling"], "difficulty": "easy", "notes": "Boolean percentage/location check."},
        {"id": "q090", "type": "boolean", "question": "Did CrossFirst say demand deposits shrank from 25% to 13% of total deposits?", "answer": "false", "evidence_keys": ["c_deposits"], "difficulty": "hard", "requires_rewrite": True, "notes": "Wrong-direction trap: evidence says demand deposits grew from 13% to 25%."},
        # ood: q091-q100
        {"id": "q091", "type": "ood", "question": "What was Alphabet's Google Cloud operating income in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Alphabet/Google Cloud segment results are not in the current five-PDF corpus."},
        {"id": "q092", "type": "ood", "question": "How many vehicles did Ford sell in Europe in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because no Ford annual report or vehicle-delivery disclosure is included."},
        {"id": "q093", "type": "ood", "question": "What was Starbucks' comparable store sales growth in China in fiscal 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Starbucks operating metrics are outside the current document set."},
        {"id": "q094", "type": "ood", "question": "What was JPMorgan Chase's CET1 capital ratio at year-end 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "Plausible finance question but unsupported because JPMorgan filings are not in this corpus."},
        {"id": "q095", "type": "ood", "question": "How much did Shell spend on renewable energy investments in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Shell energy-transition disclosures are not included in the current PDFs."},
        {"id": "q096", "type": "ood", "question": "What was Disney's direct-to-consumer operating loss in fiscal 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Disney segment reporting is not part of the current corpus."},
        {"id": "q097", "type": "ood", "question": "What was Toyota's global hybrid vehicle sales volume in fiscal 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Toyota sales-volume data is absent from the current five PDFs."},
        {"id": "q098", "type": "ood", "question": "What was Visa's payments volume growth in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": "OOD because Visa payment-network metrics are not included in the corpus."},
        {"id": "q099", "type": "ood", "question": "How many active riders did Uber report in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": "OOD because Uber user metrics are unsupported by these documents."},
        {"id": "q100", "type": "ood", "question": "What was Unilever's underlying sales growth in emerging markets in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Unilever geographic sales metrics are outside the current five-PDF set."},
    ]


def final_item(spec: dict[str, Any], evidence_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    evidence = [evidence_from_chunk(evidence_lookup[key]) for key in spec.get("evidence_keys", [])]
    source_doc = spec.get("source_doc") or (evidence[0]["doc_name"] if evidence else "N/A - not supported by current 5 PDF set")
    return {
        "id": spec["id"],
        "question": spec["question"],
        "answer": spec["answer"],
        "type": spec["type"],
        "source_doc": source_doc,
        "evidence": evidence,
        "difficulty": spec["difficulty"],
        "requires_rewrite": spec.get("requires_rewrite", False),
        "requires_multi_hop": spec.get("requires_multi_hop", False),
        "notes": spec["notes"],
    }


def build_items(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_queries = {**EVIDENCE_QUERIES, **EXTRA_EVIDENCE_QUERIES}
    evidence_lookup = {
        key: find_chunk(chunks, file_name=DOCS[doc_key], phrases=phrases)
        for key, (doc_key, phrases) in evidence_queries.items()
    }
    specs = first_50_specs() + extra_specs()
    return [final_item(spec, evidence_lookup) for spec in specs]


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

    lines = ["# RAG-Challenge Test Set Review", ""]
    for item_type in ["fact_qa", "numerical", "multi_hop", "boolean", "ood"]:
        lines.append(f"## {item_type}")
        lines.append("")
        for item in by_type.get(item_type, []):
            lines.extend(
                [
                    f"### {item['id']}",
                    "",
                    f"- question: {item['question']}",
                    f"- answer: {item['answer']}",
                    f"- source_doc: {item['source_doc']}",
                    f"- difficulty: {item['difficulty']}",
                    f"- requires_rewrite: {item['requires_rewrite']}",
                    f"- requires_multi_hop: {item['requires_multi_hop']}",
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
            lines.extend([f"- notes: {item['notes']}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the final 100-example RAG-Challenge benchmark.")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args()

    chunks = load_chunks(args.chunks)
    items = build_items(chunks)
    write_jsonl(items, args.output)
    write_review(items, args.review)

    print(f"chunks_path={args.chunks}")
    print(f"chunk_count={len(chunks)}")
    print(f"output={args.output}")
    print(f"review={args.review}")
    print("type_distribution:")
    for item_type, count in sorted(Counter(item["type"] for item in items).items()):
        print(f"  {item_type}: {count}")
    print("non_ood_source_doc_distribution:")
    for doc_name, count in sorted(Counter(item["source_doc"] for item in items if item["type"] != "ood").items()):
        print(f"  {doc_name}: {count}")


if __name__ == "__main__":
    main()

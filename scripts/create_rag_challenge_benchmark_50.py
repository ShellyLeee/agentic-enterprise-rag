#!/usr/bin/env python
"""Create a 50-example custom PDF RAG benchmark draft from local chunks.

The generator is deterministic and evidence-first: each non-OOD example points
to one or more chunks selected by explicit phrase matches against the local
RAG-Challenge index chunks JSONL. No external API is used.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_CHUNKS_PATH = Path("data/processed/rag_challenge_test_index/chunks.jsonl")
DEFAULT_OUTPUT_PATH = Path("data/eval/rag_challenge_test_set_50.jsonl")
DEFAULT_REVIEW_PATH = Path("data/eval/rag_challenge_test_set_50_review.md")
OOD_ANSWER = "Not sure based on the provided documents."

DOCS = {
    "holley": "194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf",
    "tradition": "2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf",
    "yellow": "9d7a72445aba6860402c3acce75af02dc045f74d.pdf",
    "mercia": "ac9aa244462c80705c3ff046542c02c459989742.pdf",
    "crossfirst": "e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf",
}

EVIDENCE_QUERIES = {
    "h_brand": ("holley", ["portfolio consists of over 70 brands", "Holley EFI", "represented 14%"]),
    "h_employees": ("holley", ["1,622 full-time employees", "100 temporary employees"]),
    "h_dividend": ("holley", ["do not intend to pay cash dividends", "foreseeable future"]),
    "h_acquisitions": ("holley", ["John's", "Southern Kentucky Classics", "RaceQuip"]),
    "h_net_sales": ("holley", ["$688.4 million", "compared to $692.9 million"]),
    "h_listed": ("holley", ["Common Stock", "HLLY", "New York Stock Exchange"]),
    "h_founded": ("holley", ["Founded in 1903", "high-performance automotive aftermarket products"]),
    "h_labor": ("holley", ["labor union", "collective bargaining agreements"]),
    "h_bowling": ("holley", ["48%", "Bowling Green"]),
    "t_margin": ("tradition", ["operating margin of 12.7%", "10.5% respectively"]),
    "t_dividend": ("tradition", ["cash dividend of CHF 5.50 per share", "one share", "every 100 shares"]),
    "t_desks": ("tradition", ["around 300 different desks", "pure agency model"]),
    "t_idb_gaitame": ("tradition", ["IDB adjusted underlying operating profit", "CHF 112.9m", "Gaitame.com"]),
    "t_exceptional": ("tradition", ["Net exceptional costs", "Russian invasion", "CHF 7.9m"]),
    "t_net_profit": ("tradition", ["Consolidated net profit", "CHF 97.4m", "CHF 71.5m"]),
    "y_repurchase": ("yellow", ["distributed $100.0 million", "share repurchase"]),
    "y_arrangement_net": ("yellow", ["net cash outlay of $96.1 million", "$101.0 million", "$4.9 million"]),
    "y_revenues": ("yellow", ["Total revenues", "$268.3 million", "$287.6 million"]),
    "y_declines": ("yellow", ["digital revenues", "print revenues", "Total revenue decline of 6.7%"]),
    "y_ebitda": ("yellow", ["Adjusted EBITDA decreased by $5.4 million", "$96.6 million", "36.0%"]),
    "y_pension": ("yellow", ["$24.0 million", "Defined Benefit Pension Plan"]),
    "y_warrants": ("yellow", ["Common share purchase warrants expired", "December 20, 2022"]),
    "y_ceo_metric": ("yellow", ["Chief Operating Decision Maker", "less CAPEX", "measure performance"]),
    "m_highlights": ("mercia", ["£31.4million awarded", "British Business Bank", "c.£87million"]),
    "m_cfo": ("mercia", ["£27.4m", "Profit before taxation", "£200.6m", "Net assets"]),
    "m_dividend": ("mercia", ["0.8 pence per share", "full year", "0.4 pence per share"]),
    "m_faradion_sale": ("mercia", ["Faradion was sold", "£100.0million", "£19.4million"]),
    "m_direct_portfolio": ("mercia", ["£119.6million", "direct investment portfolio", "£96.2million"]),
    "m_locations": ("mercia", ["eight regional locations", "Bristol", "Henley-in-Arden"]),
    "m_carbon": ("mercia", ["carbon-neutral company", "carbon footprint"]),
    "m_uk": ("mercia", ["We invest exclusively in the UK"]),
    "m_aum": ("mercia", ["assets under management", "operational leverage"]),
    "c_branches": ("crossfirst", ["branches are strategically located", "Kansas", "New Mexico"]),
    "c_acquisition": ("crossfirst", ["Farmers & Stockmens Bank", "$389 million of loans", "$570 million of deposits"]),
    "c_highlights": ("crossfirst", ["$ 6.6", "TOTAL ASSETS", "LOANS GREW"]),
    "c_performance": ("crossfirst", ["$68.6 million in adjusted net income", "$1.37"]),
    "c_deposits": ("crossfirst", ["demand deposits grew from 13% to 25%"]),
    "c_revenue": ("crossfirst", ["operating revenue has grown to $211 million", "$61 million"]),
    "c_npa": ("crossfirst", ["non-performing loans", "totaled $12 million", "non-performing assets"]),
    "c_first_branch": ("crossfirst", ["Since opening our first branch", "2007"]),
}


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


def find_chunk(chunks: list[dict[str, Any]], *, file_name: str, phrases: list[str]) -> dict[str, Any]:
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


def make_item(spec: dict[str, Any], evidence_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    evidence_keys = spec.get("evidence_keys", [])
    evidence = [evidence_from_chunk(evidence_lookup[key]) for key in evidence_keys]
    source_doc = spec.get("source_doc")
    if not source_doc and evidence:
        source_doc = evidence[0]["doc_name"]
    if not source_doc:
        source_doc = "N/A - not supported by current 5 PDF set"

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
        "gold_doc_ids": [] if spec["type"] == "ood" else sorted({gold_doc_id(item["doc_name"]) for item in evidence}),
        "gold_evidence_keywords": spec.get("gold_evidence_keywords", []),
    }


def item_specs() -> list[dict[str, Any]]:
    ood_source = "N/A - not supported by current 5 PDF set"
    current_docs = "Holley, Tradition, Yellow Pages, Mercia, and CrossFirst"
    return [
        # fact_qa: q001-q010
        {"id": "q001", "type": "fact_qa", "question": "Which brand did Holley identify as its largest brand in 2022?", "answer": "Holley EFI", "evidence_keys": ["h_brand"], "difficulty": "easy", "notes": "Direct fact question; evidence states Holley EFI was the largest brand and represented 14% of 2022 sales.", "gold_evidence_keywords": ["Holley EFI", "largest brand", "14%"]},
        {"id": "q002", "type": "fact_qa", "question": "In which states are CrossFirst Bank's branches strategically located?", "answer": "Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico.", "evidence_keys": ["c_branches"], "difficulty": "easy", "notes": "Direct fact question with an explicit state list in one chunk.", "gold_evidence_keywords": ["branches", "Kansas", "New Mexico"]},
        {"id": "q003", "type": "fact_qa", "question": "Which three businesses did Holley say it acquired in 2022?", "answer": "John's Ind., Inc. ('John's'), Southern Kentucky Classics ('SKC'), and Vesta Motorsports USA, Inc., d.b.a. RaceQuip ('RaceQuip').", "evidence_keys": ["h_acquisitions"], "difficulty": "medium", "requires_rewrite": True, "notes": "Question asks for businesses acquired; evidence uses formal acquisition wording and legal names.", "gold_evidence_keywords": ["John's", "Southern Kentucky Classics", "RaceQuip"]},
        {"id": "q004", "type": "fact_qa", "question": "To whom was Mercia's Faradion investment sold in January 2022?", "answer": "India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd.", "evidence_keys": ["m_faradion_sale"], "difficulty": "medium", "notes": "Adds Mercia coverage with a direct acquisition-exit fact.", "gold_evidence_keywords": ["Faradion", "Reliance New Energy Solar"]},
        {"id": "q005", "type": "fact_qa", "question": "Which UK regional locations did Mercia list for its teams?", "answer": "Bristol, Manchester, Preston, Leeds, Newcastle, Sheffield, London and Henley-in-Arden.", "evidence_keys": ["m_locations"], "difficulty": "easy", "notes": "Mercia location-list fact with all locations in one chunk.", "gold_evidence_keywords": ["Bristol", "Manchester", "Henley-in-Arden"]},
        {"id": "q006", "type": "fact_qa", "question": "What operating model does Tradition say its brokers use for revenues?", "answer": "A pure agency model in which revenues primarily consist of commissions earned by matching trades, and only if a trade is matched.", "evidence_keys": ["t_desks"], "difficulty": "medium", "requires_rewrite": True, "notes": "Question uses business wording while evidence uses the formal phrase 'pure agency model'.", "gold_evidence_keywords": ["pure agency model", "commissions", "matching trades"]},
        {"id": "q007", "type": "fact_qa", "question": "What non-GAAP measure does Yellow Pages say its CEO uses to measure performance?", "answer": "Adjusted EBITDA less CAPEX.", "evidence_keys": ["y_ceo_metric"], "difficulty": "medium", "requires_rewrite": True, "notes": "Question uses CEO/performance wording; evidence names the Chief Operating Decision Maker and metric.", "gold_evidence_keywords": ["Chief Operating Decision Maker", "Adjusted EBITDA less CAPEX"]},
        {"id": "q008", "type": "fact_qa", "question": "When did CrossFirst say it opened its first branch?", "answer": "2007.", "evidence_keys": ["c_first_branch"], "difficulty": "easy", "notes": "Direct CrossFirst chronology fact.", "gold_evidence_keywords": ["first branch", "2007"]},
        {"id": "q009", "type": "fact_qa", "question": "What trading symbol is listed for Holley's common stock?", "answer": "HLLY.", "evidence_keys": ["h_listed"], "difficulty": "easy", "notes": "Direct securities-listing fact from Holley's cover page.", "gold_evidence_keywords": ["Common Stock", "HLLY", "New York Stock Exchange"]},
        {"id": "q010", "type": "fact_qa", "question": "What organization awarded £31.4 million to Mercia's equity and debt funds?", "answer": "The British Business Bank ('BBB').", "evidence_keys": ["m_highlights"], "difficulty": "easy", "notes": "Mercia operational highlight with clear awarding organization.", "gold_evidence_keywords": ["£31.4million", "British Business Bank"]},
        # numerical: q011-q020
        {"id": "q011", "type": "numerical", "question": "As of December 31, 2022, how many full-time and temporary employees did Holley employ?", "answer": "1,622 full-time employees and 100 temporary employees.", "evidence_keys": ["h_employees"], "difficulty": "easy", "notes": "Explicit headcount figures; no unit conversion is needed.", "gold_evidence_keywords": ["1,622 full-time employees", "100 temporary employees"]},
        {"id": "q012", "type": "numerical", "question": "What were Tradition's underlying operating profitability margins for 2022 and 2021?", "answer": "12.7% in 2022 and 10.5% in 2021.", "evidence_keys": ["t_margin"], "difficulty": "medium", "requires_rewrite": True, "notes": "Question says profitability margins while evidence says operating margin; no unit conversion is needed.", "gold_evidence_keywords": ["operating margin", "12.7%", "10.5%"]},
        {"id": "q013", "type": "numerical", "question": "What were Holley's net sales for 2022 and 2021?", "answer": "$688.4 million in 2022 and $692.9 million in 2021.", "evidence_keys": ["h_net_sales"], "difficulty": "easy", "notes": "Financial amount question with explicit dollars and years; no unit conversion is needed.", "gold_evidence_keywords": ["$688.4 million", "$692.9 million"]},
        {"id": "q014", "type": "numerical", "question": "What total revenues did Yellow Pages report for 2022 versus 2021?", "answer": "$268.3 million in 2022 compared with $287.6 million in 2021.", "evidence_keys": ["y_revenues"], "difficulty": "easy", "notes": "Financial amount question in Canadian dollars; no unit conversion is needed.", "gold_evidence_keywords": ["$268.3 million", "$287.6 million"]},
        {"id": "q015", "type": "numerical", "question": "What profit before taxation and net assets did Mercia report in its 2022 highlights?", "answer": "£27.4m profit before taxation and £200.6m net assets.", "evidence_keys": ["m_cfo"], "difficulty": "easy", "notes": "Mercia numerical highlight; no unit conversion is needed.", "gold_evidence_keywords": ["£27.4m", "£200.6m"]},
        {"id": "q016", "type": "numerical", "question": "What was Mercia's direct investment portfolio value as at 31 March 2022 and the 2021 comparator?", "answer": "£119.6 million in 2022, compared with £96.2 million in 2021.", "evidence_keys": ["m_direct_portfolio"], "difficulty": "medium", "notes": "Mercia portfolio valuation with explicit date and comparator; no unit conversion is needed.", "gold_evidence_keywords": ["£119.6million", "£96.2million"]},
        {"id": "q017", "type": "numerical", "question": "What adjusted net income and adjusted diluted EPS did CrossFirst report for 2022?", "answer": "$68.6 million in adjusted net income and adjusted diluted earnings per share of $1.37.", "evidence_keys": ["c_performance"], "difficulty": "medium", "notes": "CrossFirst financial-performance numbers; no unit conversion is needed.", "gold_evidence_keywords": ["$68.6 million", "$1.37"]},
        {"id": "q018", "type": "numerical", "question": "By how much did Yellow Pages' Adjusted EBITDA change, and what was the 2022 Adjusted EBITDA amount?", "answer": "Adjusted EBITDA decreased by $5.4 million, or 5.3%, to $96.6 million.", "evidence_keys": ["y_ebitda"], "difficulty": "medium", "notes": "Numeric metric includes amount, percentage change, and resulting value; no unit conversion is needed.", "gold_evidence_keywords": ["$5.4 million", "5.3%", "$96.6 million"]},
        {"id": "q019", "type": "numerical", "question": "What cash dividend per share did Tradition's Board seek approval to pay?", "answer": "CHF 5.50 per share.", "evidence_keys": ["t_dividend"], "difficulty": "easy", "notes": "Dividend amount question; no unit conversion is needed.", "gold_evidence_keywords": ["CHF 5.50 per share"]},
        {"id": "q020", "type": "numerical", "question": "What voluntary contribution did Yellow Pages advance to its Defined Benefit Pension Plan wind-up deficit?", "answer": "$24.0 million.", "evidence_keys": ["y_pension"], "difficulty": "easy", "notes": "Pension contribution amount; no unit conversion is needed.", "gold_evidence_keywords": ["$24.0 million", "Defined Benefit Pension Plan"]},
        # multi_hop: q021-q030
        {"id": "q021", "type": "multi_hop", "question": "What evidence shows Holley was both a broad brand portfolio company and a sizable employer at the end of 2022?", "answer": "Holley's portfolio had over 70 brands across 30 product categories, and it employed 1,622 full-time employees plus 100 temporary employees as of December 31, 2022.", "evidence_keys": ["h_brand", "h_employees"], "difficulty": "medium", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines Holley's brand portfolio scale and employee headcount from two chunks/pages.", "gold_evidence_keywords": ["over 70 brands", "30 product categories", "1,622 full-time employees"]},
        {"id": "q022", "type": "multi_hop", "question": "Which acquisition expanded CrossFirst in 2022, and what adjusted diluted EPS and adjusted ROE did CrossFirst report for that year?", "answer": "CrossFirst completed the acquisition of Farmers & Stockmens Bank ('Central'); for the year it delivered $1.37 in adjusted diluted earnings per share and adjusted ROE improved to 11.11% in 2022.", "evidence_keys": ["c_acquisition", "c_highlights"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Uses one chunk for the acquisition and another for adjusted EPS/ROE.", "gold_evidence_keywords": ["Farmers & Stockmens Bank", "$1.37", "11.11%"]},
        {"id": "q023", "type": "multi_hop", "question": "How did Mercia's Faradion exit relate to the reported value of its direct investment portfolio?", "answer": "Mercia sold Faradion in January 2022 for £100.0 million, generating £19.4 million of cash proceeds to Mercia's balance sheet; as at 31 March 2022, the Group's direct investment portfolio was valued at £119.6 million.", "evidence_keys": ["m_faradion_sale", "m_direct_portfolio"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Mercia multi-hop across exit proceeds and portfolio valuation chunks.", "gold_evidence_keywords": ["Faradion", "£100.0million", "£19.4million", "£119.6million"]},
        {"id": "q024", "type": "multi_hop", "question": "What shareholder cash action did Yellow Pages take in 2022, and what was the net cash outlay after treasury-share cancellation?", "answer": "Yellow Pages distributed $100.0 million to shareholders by way of a share repurchase; the arrangement had a net cash outlay of $96.1 million after reducing the $101.0 million cash outlay by $4.9 million for treasury-share cancellation.", "evidence_keys": ["y_repurchase", "y_arrangement_net"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Uses the high-level shareholder distribution chunk plus arrangement details for the net cash outlay.", "gold_evidence_keywords": ["distributed $100.0 million", "net cash outlay", "$96.1 million"]},
        {"id": "q025", "type": "multi_hop", "question": "What did Tradition report about operating profitability and shareholder distributions for the year?", "answer": "Tradition reported adjusted underlying operating profit of CHF 130.3m with an operating margin of 12.7%, and the Board sought approval for a CHF 5.50 per share cash dividend plus one treasury share for every 100 shares held.", "evidence_keys": ["t_margin", "t_dividend"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines operating profitability and shareholder distribution evidence.", "gold_evidence_keywords": ["CHF 130.3m", "12.7%", "CHF 5.50", "one share"]},
        {"id": "q026", "type": "multi_hop", "question": "How do Holley's founding history and 2022 acquisition activity describe the company's automotive aftermarket strategy?", "answer": "Holley was founded in 1903 and describes itself as a designer, marketer, and manufacturer of high-performance automotive aftermarket products; it also added to its brand lineup through 2022 acquisitions including John's, SKC, and RaceQuip.", "evidence_keys": ["h_founded", "h_acquisitions"], "difficulty": "medium", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines company background and acquisition activity from two Holley chunks.", "gold_evidence_keywords": ["Founded in 1903", "automotive aftermarket", "John's", "RaceQuip"]},
        {"id": "q027", "type": "multi_hop", "question": "What evidence connects Mercia's UK-only investment focus with its ESG-related operating milestone?", "answer": "Mercia states that it invests exclusively in the UK and also says it measured and offset its carbon footprint to become a carbon-neutral company.", "evidence_keys": ["m_uk", "m_carbon"], "difficulty": "medium", "requires_multi_hop": True, "notes": "Mercia multi-hop over investment focus and ESG/carbon-neutral evidence from separate chunks.", "gold_evidence_keywords": ["exclusively in the UK", "carbon-neutral company"]},
        {"id": "q028", "type": "multi_hop", "question": "What evidence shows CrossFirst had both a multi-state branch footprint and improved deposit mix?", "answer": "CrossFirst's branches were strategically located in Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico, and demand deposits grew from 13% to 25% of total deposits.", "evidence_keys": ["c_branches", "c_deposits"], "difficulty": "medium", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines geographic footprint and deposit mix from separate CrossFirst chunks.", "gold_evidence_keywords": ["Kansas", "New Mexico", "13% to 25%"]},
        {"id": "q029", "type": "multi_hop", "question": "How did Yellow Pages describe both revenue pressure and profitability for 2022?", "answer": "Yellow Pages reported total revenues decreased 6.7% to $268.3 million from $287.6 million, while Adjusted EBITDA decreased to $96.6 million and the adjusted EBITDA margin increased to 36.0%.", "evidence_keys": ["y_revenues", "y_ebitda"], "difficulty": "hard", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines revenue and profitability chunks to test synthesis under mixed signals.", "gold_evidence_keywords": ["6.7%", "$268.3 million", "$96.6 million", "36.0%"]},
        {"id": "q030", "type": "multi_hop", "question": "What evidence shows Mercia had both financial resources and an ESG-related operating milestone?", "answer": "Mercia reported £61.3m of cash in its 2022 highlights and said it measured and offset its carbon footprint to become a carbon-neutral company.", "evidence_keys": ["m_cfo", "m_carbon"], "difficulty": "medium", "requires_rewrite": True, "requires_multi_hop": True, "notes": "Combines Mercia financial highlight and ESG/carbon-neutral evidence.", "gold_evidence_keywords": ["£61.3m", "carbon-neutral company"]},
        # boolean: q031-q040
        {"id": "q031", "type": "boolean", "question": "Does Holley say it plans to pay cash dividends for the foreseeable future?", "answer": "false", "evidence_keys": ["h_dividend"], "difficulty": "easy", "notes": "Evidence directly states Holley does not intend to pay cash dividends for the foreseeable future.", "gold_evidence_keywords": ["do not intend", "cash dividends"]},
        {"id": "q032", "type": "boolean", "question": "Did Yellow Pages distribute $100.0 million to shareholders through a share repurchase in 2022?", "answer": "true", "evidence_keys": ["y_repurchase"], "difficulty": "easy", "notes": "Direct yes/no question supported by Yellow Pages' statutory plan of arrangement language.", "gold_evidence_keywords": ["distributed $100.0 million", "share repurchase"]},
        {"id": "q033", "type": "boolean", "question": "Did Mercia say it became a carbon-neutral company?", "answer": "true", "evidence_keys": ["m_carbon"], "difficulty": "easy", "notes": "Boolean Mercia ESG item with explicit carbon-neutral wording.", "gold_evidence_keywords": ["carbon-neutral company"]},
        {"id": "q034", "type": "boolean", "question": "Was Mercia's recommended full-year dividend 0.8 pence per share?", "answer": "true", "evidence_keys": ["m_dividend"], "difficulty": "easy", "notes": "Boolean numerical check on Mercia dividend language.", "gold_evidence_keywords": ["0.8 pence per share"]},
        {"id": "q035", "type": "boolean", "question": "Did CrossFirst report non-performing loans of $12 million as of December 31, 2022?", "answer": "true", "evidence_keys": ["c_npa"], "difficulty": "easy", "notes": "Boolean numeric fact from CrossFirst risk discussion.", "gold_evidence_keywords": ["non-performing loans", "$12 million"]},
        {"id": "q036", "type": "boolean", "question": "Did Tradition propose an exceptional distribution of one treasury share for every 100 shares held?", "answer": "true", "evidence_keys": ["t_dividend"], "difficulty": "easy", "notes": "Boolean shareholder distribution item.", "gold_evidence_keywords": ["one share", "every 100 shares"]},
        {"id": "q037", "type": "boolean", "question": "Were Holley's common stock and warrants listed on the New York Stock Exchange?", "answer": "true", "evidence_keys": ["h_listed"], "difficulty": "easy", "notes": "Boolean securities-listing item based on cover-page table.", "gold_evidence_keywords": ["Common Stock", "Warrants", "New York Stock Exchange"]},
        {"id": "q038", "type": "boolean", "question": "Did Yellow Pages' common share purchase warrants expire on December 20, 2022?", "answer": "true", "evidence_keys": ["y_warrants"], "difficulty": "easy", "notes": "Boolean expiration-date item.", "gold_evidence_keywords": ["warrants expired", "December 20, 2022"]},
        {"id": "q039", "type": "boolean", "question": "Were Holley's employees represented by a labor union?", "answer": "false", "evidence_keys": ["h_labor"], "difficulty": "easy", "notes": "Evidence says employees were not subject to collective bargaining agreements or represented by a labor union.", "gold_evidence_keywords": ["labor union", "collective bargaining agreements"]},
        {"id": "q040", "type": "boolean", "question": "Did Mercia say it invests exclusively in the UK?", "answer": "true", "evidence_keys": ["m_uk"], "difficulty": "easy", "notes": "Boolean Mercia investment-focus item.", "gold_evidence_keywords": ["invest exclusively in the UK"]},
        # ood: q041-q050
        {"id": "q041", "type": "ood", "question": "What was Apple's research and development expense in fiscal 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": f"OOD because the current PDF set contains {current_docs} reports, not Apple financial statements."},
        {"id": "q042", "type": "ood", "question": "What greenhouse gas emissions reduction target did Tesla set for 2030 in these documents?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": f"OOD because none of the current five PDFs is a Tesla report or provides sufficient evidence for Tesla's 2030 emissions targets."},
        {"id": "q043", "type": "ood", "question": "What was NVIDIA's data center revenue in fiscal 2024?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": f"OOD because the current PDF set covers {current_docs}, not NVIDIA."},
        {"id": "q044", "type": "ood", "question": "How much revenue did Microsoft Azure generate in fiscal 2023?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because the current documents do not include Microsoft segment reporting."},
        {"id": "q045", "type": "ood", "question": "What capital expenditures did Amazon report for AWS infrastructure in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Amazon/AWS financial disclosures are not part of the current five-PDF corpus."},
        {"id": "q046", "type": "ood", "question": "How many paid subscribers did Netflix report at the end of 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": "OOD because no Netflix annual report or subscriber disclosure is included in the current corpus."},
        {"id": "q047", "type": "ood", "question": "What was Meta's Facebook daily active users figure for December 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": "OOD because Meta platform metrics are not covered by the current PDF set."},
        {"id": "q048", "type": "ood", "question": "What was Coca-Cola's net operating revenue in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": "OOD because the current five PDFs do not include Coca-Cola filings."},
        {"id": "q049", "type": "ood", "question": "How many commercial airplanes did Boeing deliver in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "easy", "notes": "OOD because Boeing delivery data is outside the current five-PDF corpus."},
        {"id": "q050", "type": "ood", "question": "What was Pfizer's Comirnaty revenue in 2022?", "answer": OOD_ANSWER, "source_doc": ood_source, "difficulty": "medium", "notes": "OOD because Pfizer product revenue disclosures are not included in the current documents."},
    ]


def build_items(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_lookup = {
        key: find_chunk(chunks, file_name=DOCS[doc_key], phrases=phrases)
        for key, (doc_key, phrases) in EVIDENCE_QUERIES.items()
    }
    return [make_item(spec, evidence_lookup) for spec in item_specs()]


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

    lines = ["# RAG-Challenge Test Set 50 Review", ""]
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
    parser = argparse.ArgumentParser(description="Create a 50-example RAG-Challenge benchmark draft.")
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
    for item_type, count in sorted(Counter(item["type"] for item in items).items()):
        print(f"  {item_type}: {count}")
    print("non_ood_source_doc_distribution:")
    for doc_name, count in sorted(Counter(item["source_doc"] for item in items if item["type"] != "ood").items()):
        print(f"  {doc_name}: {count}")


if __name__ == "__main__":
    main()

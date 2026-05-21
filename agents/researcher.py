"""Researcher 에이전트.

흐름:
1. tools.sources.search_all 로 도메인별 후보 Document 수집
2. 각 Document의 URL을 fetch 해 본문을 저장
3. LLM에게 summary/key_claims 채우게 한 뒤 Document 갱신
"""
from __future__ import annotations

import json
from pathlib import Path

from agents.llm import SUBAGENT_MODEL, call, load_system_prompt
from agents.models import Citation, Document, Query
from tools import fetch, sources

RAW_DIR = Path(__file__).resolve().parent.parent / "storage" / "raw"


def _enrich_with_llm(query: Query, doc: Document, body: str) -> Document:
    system = load_system_prompt("researcher")
    user = (
        f"주제: {query.text}\n"
        f"문서 메타: {json.dumps(doc.metadata.model_dump(), ensure_ascii=False)}\n"
        f"URL: {doc.source.url}\n\n"
        f"본문 발췌(최대 8000자):\n{body}\n\n"
        "다음 JSON 객체 1개만 반환하시오. 다른 텍스트 금지.\n"
        '{ "summary": "3~5문장", "key_claims": ["...", "..."], '
        '"citations": [{"text":"원문 인용","anchor":""}], "tags": ["..."] }'
    )
    try:
        data = call(system, user, model=SUBAGENT_MODEL, expect_json=True)
    except Exception as e:
        print(f"[researcher] enrich failed for {doc.source.url}: {e}")
        return doc
    doc.content.summary = data.get("summary") or doc.content.summary
    doc.content.key_claims = data.get("key_claims") or []
    doc.citations = [Citation(**c) for c in (data.get("citations") or [])]
    doc.tags = data.get("tags") or []
    return doc


def run(query: Query, *, per_domain: int = 5, enrich: bool = True) -> list[Document]:
    candidates = sources.search_all(query.text, query.domains, limit=per_domain)
    for d in candidates:
        d.query_id = query.id

    if not enrich:
        return candidates

    enriched: list[Document] = []
    for d in candidates:
        body = fetch.fetch_text(d.source.url)
        d.content.raw_path = fetch.save_raw(d.id, body, RAW_DIR)
        enriched.append(_enrich_with_llm(query, d, body))
    return enriched

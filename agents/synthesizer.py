"""Synthesizer 에이전트 — Document 배열 → Markdown 보고서."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from agents.llm import ORCHESTRATOR_MODEL, call, load_system_prompt
from agents.models import Document, Query, Report

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def _slug(text: str) -> str:
    s = re.sub(r"[^\w가-힣\- ]+", "", text).strip().lower()
    s = re.sub(r"\s+", "-", s)
    return s[:60] or "report"


def _citation_line(i: int, d: Document) -> str:
    authors = ", ".join(d.metadata.authors[:3])
    if len(d.metadata.authors) > 3:
        authors += " 외"
    year = d.metadata.year or "n.d."
    venue = d.metadata.venue or d.source.type
    return f"[^{i}]: {authors} ({year}). _{d.metadata.title}_. {venue}. {d.source.url}"


def _fallback_markdown(query: Query, docs: list[Document]) -> str:
    lines = [
        f"# {query.text} — 리서치 브리프\n",
        f"생성일: {date.today()}  ·  쿼리 ID: {query.id}  ·  문서 수: {len(docs)}\n",
        "## TL;DR",
    ]
    for d in docs[:5]:
        if d.content.summary:
            lines.append(f"- {d.content.summary.splitlines()[0][:160]}")
    lines.append("\n## 핵심 발견")
    for i, d in enumerate(docs, 1):
        lines.append(f"### {i}) {d.metadata.title or d.source.url}")
        lines.append(f"{d.content.summary or '(요약 없음)'} [^{i}]")
        for claim in d.content.key_claims[:3]:
            lines.append(f"- {claim}")
        lines.append("")
    lines.append("## 출처")
    for i, d in enumerate(docs, 1):
        lines.append(_citation_line(i, d))
    return "\n".join(lines) + "\n"


def _llm_markdown(query: Query, docs: list[Document]) -> str:
    system = load_system_prompt("synthesizer")
    payload = [
        {
            "n": i,
            "title": d.metadata.title,
            "year": d.metadata.year,
            "url": d.source.url,
            "authors": d.metadata.authors,
            "summary": d.content.summary,
            "key_claims": d.content.key_claims,
            "credibility": d.credibility.score,
        }
        for i, d in enumerate(docs, 1)
    ]
    user = (
        f"주제: {query.text}\n"
        f"오늘 날짜: {date.today()}\n\n"
        "다음 문서들을 바탕으로 한국어 리서치 브리프를 Markdown 으로 작성하시오. "
        "모든 사실 진술 끝에 [^n] 각주를 부착하고, 출처 섹션은 자동으로 추가될 것이므로 "
        "본문에서만 [^n] 을 인용 위치에 사용. 응답은 순수 Markdown(코드펜스 X)만.\n\n"
        f"문서 JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    body = call(system, user, model=ORCHESTRATOR_MODEL, max_tokens=4096)
    body = body.strip()
    sources_md = "\n".join(_citation_line(i, d) for i, d in enumerate(docs, 1))
    if "## 출처" not in body:
        body += "\n\n## 출처\n" + sources_md
    else:
        body += "\n\n" + sources_md
    return body + "\n"


def run(query: Query, docs: list[Document], *, use_llm: bool = True) -> Report:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md = ""
    if use_llm:
        try:
            md = _llm_markdown(query, docs)
        except Exception as e:
            print(f"[synthesizer] LLM failed, falling back: {e}")
    if not md:
        md = _fallback_markdown(query, docs)

    out = REPORTS_DIR / f"{date.today()}-{_slug(query.text)}.md"
    out.write_text(md, encoding="utf-8")
    return Report(
        query_id=query.id,
        doc_ids=[d.id for d in docs],
        markdown_path=str(out),
    )

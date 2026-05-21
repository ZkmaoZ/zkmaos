"""Critic 에이전트 — Document 신뢰도 평가.

규칙 기반 점수와 LLM 기반 평가를 조합. LLM 호출 실패 시 규칙만으로도 동작.
"""
from __future__ import annotations

import json
from datetime import datetime

from agents.llm import SUBAGENT_MODEL, call, load_system_prompt
from agents.models import Credibility, Document


def _rule_score(d: Document) -> Credibility:
    year = d.metadata.year or 0
    age = max(0, datetime.now().year - year) if year else 99
    recency = 1.0 if age <= 1 else 0.7 if age <= 3 else 0.4 if age <= 5 else 0.2
    authority = {
        "paper": 1.0, "report": 0.8, "news": 0.6,
        "web": 0.5, "market": 0.7, "patent": 0.9,
    }.get(d.source.type, 0.5)
    peer = 1.0 if d.source.type == "paper" else 0.0
    score = round(0.4 * recency + 0.4 * authority + 0.2 * peer, 3)
    return Credibility(
        score=score,
        factors={"recency": recency, "source_authority": authority, "peer_reviewed": peer},
    )


def run(docs: list[Document], *, use_llm: bool = True) -> list[Document]:
    for d in docs:
        d.credibility = _rule_score(d)
        if d.credibility.score < 0.4:
            d.credibility.exclude_reason = "낮은 규칙 점수"

    if not use_llm:
        return docs

    system = load_system_prompt("critic")
    payload = [
        {
            "id": d.id, "url": d.source.url, "title": d.metadata.title,
            "year": d.metadata.year, "summary": d.content.summary,
            "rule_score": d.credibility.score,
        }
        for d in docs
    ]
    user = (
        "다음 문서들에 대해 conflict(같은 주제 다른 주장)을 검출하고, "
        "rule_score 가 0.4 이상인 문서 중 신뢰도가 의심되는 것을 표시하시오.\n"
        "JSON 배열만 반환: [{\"id\":\"...\",\"conflicts\":[\"id\"], "
        "\"exclude_reason\":\"\"}]\n\n"
        f"입력:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    try:
        result = call(system, user, model=SUBAGENT_MODEL, expect_json=True)
    except Exception as e:
        print(f"[critic] LLM evaluation skipped: {e}")
        return docs

    by_id = {d.id: d for d in docs}
    for item in result:
        d = by_id.get(item.get("id"))
        if not d:
            continue
        if reason := item.get("exclude_reason"):
            d.credibility.exclude_reason = reason
        if conflicts := item.get("conflicts"):
            d.credibility.factors["conflicts"] = float(len(conflicts))
    return docs


def kept(docs: list[Document]) -> list[Document]:
    return [d for d in docs if not d.credibility.exclude_reason]

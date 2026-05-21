"""Research orchestrator — Phase 1 MVP skeleton.

실행 예:
    python -m agents.orchestrator "LLM 기반 에이전트 평가 벤치마크 동향"
"""
from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


@dataclass
class Query:
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domains: list[str] = field(default_factory=lambda: ["paper", "news", "market", "patent"])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def run(query_text: str) -> Path:
    query = Query(text=query_text)
    # TODO Phase 2: Anthropic SDK 로 researcher → critic → synthesizer 호출 체인
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{datetime.now().date()}-{query.id[:8]}.md"
    out.write_text(
        f"# {query_text}\n\n"
        f"_생성 예정 — Phase 2에서 채워집니다._\n\n"
        f"- query_id: {query.id}\n"
        f"- created_at: {query.created_at}\n",
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -m agents.orchestrator '<주제>'", file=sys.stderr)
        sys.exit(1)
    path = run(" ".join(sys.argv[1:]))
    print(f"wrote {path}")

"""CLI 진입점.

사용법:
    python -m agents.run "주제"
    python -m agents.run "주제" --no-llm        # 검색·규칙만, API 키 불필요
    python -m agents.run "주제" --per-domain 3
"""
from __future__ import annotations

import argparse
import sys

from agents.orchestrator import run


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="agents.run")
    p.add_argument("topic", nargs="+", help="조사 주제")
    p.add_argument("--per-domain", type=int, default=5)
    p.add_argument(
        "--no-llm",
        action="store_true",
        help="LLM 호출 없이 검색·규칙·폴백 보고서만",
    )
    args = p.parse_args(argv)
    report = run(
        " ".join(args.topic),
        per_domain=args.per_domain,
        use_llm=not args.no_llm,
    )
    print(report.markdown_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Anthropic SDK 얇은 래퍼.

- 시스템 프롬프트는 .claude/agents/*.md 의 본문을 그대로 재활용 (단일 출처 원칙)
- JSON 출력을 강제하기 위해 응답의 첫 번째 ```...``` 또는 [/{ 시작 블록을 파싱
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / ".claude" / "agents"

ORCHESTRATOR_MODEL = os.getenv("ZKMAOS_ORCHESTRATOR_MODEL", "claude-opus-4-7")
SUBAGENT_MODEL = os.getenv("ZKMAOS_SUBAGENT_MODEL", "claude-sonnet-4-6")


def load_system_prompt(name: str) -> str:
    """`.claude/agents/<name>.md` 의 frontmatter 이후 본문을 시스템 프롬프트로 사용."""
    path = AGENT_DIR / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        _, _, rest = text.partition("\n---\n")
        return (rest or text).strip()
    return text.strip()


def _extract_json(text: str) -> Any:
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    candidate = fence.group(1) if fence else text
    start = min(
        (i for i in [candidate.find("["), candidate.find("{")] if i != -1),
        default=-1,
    )
    if start == -1:
        raise ValueError(f"no JSON found in LLM output: {text[:200]}...")
    snippet = candidate[start:]
    # JSON 직후의 잡문 제거: 균형 잡힌 괄호까지만 사용
    depth = 0
    end = -1
    in_str = False
    esc = False
    open_ch, close_ch = ("[", "]") if snippet[0] == "[" else ("{", "}")
    for i, ch in enumerate(snippet):
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
        elif not in_str:
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    snippet = snippet[:end] if end != -1 else snippet
    return json.loads(snippet)


def call(
    system: str,
    user: str,
    *,
    model: str = SUBAGENT_MODEL,
    max_tokens: int = 4096,
    expect_json: bool = False,
) -> Any:
    """Anthropic Messages API 호출. 임포트는 함수 안에서(테스트 친화)."""
    from anthropic import Anthropic

    client = Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    if expect_json:
        return _extract_json(text)
    return text

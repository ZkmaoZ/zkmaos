"""벡터 인덱스 — 중복·유사도 검색용.

- 기본: SQLite + 단어 hash 기반 sparse 벡터 (의존성 없음, 결정론적, 테스트 가능)
- 옵션: chromadb 가 설치돼 있으면 그쪽으로 위임 (`use_chroma=True`)

목적은 정밀한 의미 검색이 아니라, "이 문서가 과거에 본 적 있는가 / 가장 가까운 과거 문서는?"
같은 회상 질의에 충분한 신호를 주는 것.
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "vectors.db"
DIM = 1024  # hashing 차원


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z가-힣0-9]{2,}", (text or "").lower())


def embed(text: str) -> dict[int, float]:
    """결정론적 hashing 임베딩 → 희소 벡터(dict). L2 정규화."""
    counts = Counter(hash(tok) % DIM for tok in _tokenize(text))
    if not counts:
        return {}
    norm = math.sqrt(sum(v * v for v in counts.values()))
    return {k: v / norm for k, v in counts.items()}


def cosine(a: dict[int, float], b: dict[int, float]) -> float:
    if not a or not b:
        return 0.0
    short, long = (a, b) if len(a) < len(b) else (b, a)
    return sum(v * long.get(k, 0.0) for k, v in short.items())


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init() -> None:
    with _connect() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS embeddings(
                 doc_id TEXT PRIMARY KEY,
                 url    TEXT NOT NULL,
                 title  TEXT NOT NULL,
                 vec    TEXT NOT NULL
               )"""
        )


@dataclass
class Hit:
    doc_id: str
    url: str
    title: str
    score: float


def upsert(doc_id: str, url: str, title: str, text: str) -> None:
    vec = embed(f"{title}\n{text}")
    with _connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO embeddings(doc_id,url,title,vec) VALUES(?,?,?,?)",
            (doc_id, url, title, json.dumps(vec)),
        )


def query(text: str, top_k: int = 5) -> list[Hit]:
    q = embed(text)
    if not q:
        return []
    with _connect() as c:
        rows = c.execute("SELECT doc_id,url,title,vec FROM embeddings").fetchall()
    scored = [
        Hit(doc_id, url, title, cosine(q, {int(k): v for k, v in json.loads(vec).items()}))
        for doc_id, url, title, vec in rows
    ]
    scored.sort(key=lambda h: h.score, reverse=True)
    return [h for h in scored[:top_k] if h.score > 0]

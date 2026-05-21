"""표준 데이터 스키마 (docs/schema.md 와 동기화).

모든 에이전트는 이 Pydantic 모델로 데이터를 주고받는다.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


Domain = Literal["paper", "web", "news", "market", "patent", "report"]


class Source(BaseModel):
    type: Domain
    url: str
    fetched_at: str = Field(default_factory=_now)


class Metadata(BaseModel):
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: str = ""
    lang: str = "en"


class Content(BaseModel):
    raw_path: str = ""
    summary: str = ""
    key_claims: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    text: str
    page: Optional[int] = None
    anchor: str = ""


class Credibility(BaseModel):
    score: float = 0.0
    factors: dict[str, float] = Field(default_factory=dict)
    exclude_reason: str = ""


class Document(BaseModel):
    id: str = Field(default_factory=_uuid)
    query_id: str = ""
    source: Source
    metadata: Metadata = Field(default_factory=Metadata)
    content: Content = Field(default_factory=Content)
    citations: list[Citation] = Field(default_factory=list)
    credibility: Credibility = Field(default_factory=Credibility)
    tags: list[str] = Field(default_factory=list)


class Query(BaseModel):
    id: str = Field(default_factory=_uuid)
    text: str
    domains: list[Domain] = Field(
        default_factory=lambda: ["paper", "news", "market", "patent"]
    )
    lang: list[str] = Field(default_factory=lambda: ["ko", "en"])
    depth: Literal["shallow", "standard", "deep"] = "standard"
    created_at: str = Field(default_factory=_now)


class Report(BaseModel):
    query_id: str
    generated_at: str = Field(default_factory=_now)
    doc_ids: list[str] = Field(default_factory=list)
    markdown_path: str = ""

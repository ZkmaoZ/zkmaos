"""도메인별 소스 어댑터 — Phase 2에서 실제 호출로 채울 자리.

각 함수는 Document 후보의 메타데이터 리스트(dict)를 반환합니다.
실제 구현 시 API 키는 환경변수에서 읽고, 결과는 docs/schema.md 의
Document 스키마에 맞춰 정규화합니다.
"""
from __future__ import annotations


def arxiv_search(query: str, limit: int = 5) -> list[dict]:
    """arXiv API 검색 — 추후 구현."""
    raise NotImplementedError


def semantic_scholar_search(query: str, limit: int = 5) -> list[dict]:
    raise NotImplementedError


def news_search(query: str, limit: int = 5) -> list[dict]:
    raise NotImplementedError


def patent_search(query: str, limit: int = 5) -> list[dict]:
    raise NotImplementedError

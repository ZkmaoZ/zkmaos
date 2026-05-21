"""SQLite 영속화 — Phase 2에서 구현.

테이블 스케치:
  queries(id, text, created_at, depth)
  documents(id, query_id, source_type, url, fetched_at, metadata_json,
            summary, credibility, exclude_reason)
  citations(id, doc_id, text, page, anchor)
  reports(query_id, markdown_path, generated_at)
"""
from __future__ import annotations

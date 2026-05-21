"""SQLite 영속화.

테이블:
  queries(id, text, created_at, depth)
  documents(id, query_id, source_type, url, fetched_at, metadata_json,
            summary, credibility_json, exclude_reason)
  reports(query_id, markdown_path, generated_at)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from agents.models import Document, Query, Report

DB_PATH = Path(__file__).resolve().parent / "zkmaos.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS queries (
              id TEXT PRIMARY KEY,
              text TEXT NOT NULL,
              created_at TEXT NOT NULL,
              depth TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS documents (
              id TEXT PRIMARY KEY,
              query_id TEXT NOT NULL REFERENCES queries(id),
              source_type TEXT NOT NULL,
              url TEXT NOT NULL,
              fetched_at TEXT NOT NULL,
              metadata_json TEXT NOT NULL,
              summary TEXT NOT NULL,
              credibility_json TEXT NOT NULL,
              exclude_reason TEXT NOT NULL DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS idx_documents_query ON documents(query_id);
            CREATE TABLE IF NOT EXISTS reports (
              query_id TEXT PRIMARY KEY REFERENCES queries(id),
              markdown_path TEXT NOT NULL,
              generated_at TEXT NOT NULL
            );
            """
        )


def save_query(q: Query) -> None:
    with connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO queries(id,text,created_at,depth) VALUES(?,?,?,?)",
            (q.id, q.text, q.created_at, q.depth),
        )


def save_documents(docs: list[Document]) -> None:
    with connect() as c:
        c.executemany(
            """INSERT OR REPLACE INTO documents
               (id,query_id,source_type,url,fetched_at,metadata_json,
                summary,credibility_json,exclude_reason)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            [
                (
                    d.id,
                    d.query_id,
                    d.source.type,
                    d.source.url,
                    d.source.fetched_at,
                    json.dumps(d.metadata.model_dump(), ensure_ascii=False),
                    d.content.summary,
                    json.dumps(d.credibility.model_dump(), ensure_ascii=False),
                    d.credibility.exclude_reason,
                )
                for d in docs
            ],
        )


def save_report(r: Report) -> None:
    with connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO reports(query_id,markdown_path,generated_at) VALUES(?,?,?)",
            (r.query_id, r.markdown_path, r.generated_at),
        )

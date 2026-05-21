"""테스트 전역 설정 — DB/보고서/raw 경로를 tmp 로 격리."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from agents import diff, researcher, synthesizer
    from storage import db, vectors

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(vectors, "DB_PATH", tmp_path / "vectors.db")
    monkeypatch.setattr(researcher, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(synthesizer, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(diff, "DIFF_DIR", tmp_path / "reports" / "diffs")
    return tmp_path

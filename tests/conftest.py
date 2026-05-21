"""테스트 전역 설정 — DB/보고서/raw 경로를 tmp 로 격리."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from agents import researcher, synthesizer
    from storage import db

    db_path = tmp_path / "test.db"
    raw_dir = tmp_path / "raw"
    reports_dir = tmp_path / "reports"

    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(researcher, "RAW_DIR", raw_dir)
    monkeypatch.setattr(synthesizer, "REPORTS_DIR", reports_dir)
    return tmp_path

from pathlib import Path

from agents import synthesizer
from agents.models import Document, Query, Source


def _doc(title: str, summary: str = "") -> Document:
    d = Document(source=Source(type="paper", url=f"https://x/{title}"))
    d.metadata.title = title
    d.metadata.authors = ["Alice", "Bob"]
    d.metadata.year = 2025
    d.content.summary = summary or f"{title} 요약"
    d.content.key_claims = [f"{title} claim1", f"{title} claim2"]
    return d


def test_fallback_markdown_renders_all_sections():
    q = Query(text="테스트 주제")
    docs = [_doc("A"), _doc("B")]
    md = synthesizer._fallback_markdown(q, docs)
    assert "테스트 주제" in md
    assert "## TL;DR" in md
    assert "## 핵심 발견" in md
    assert "## 출처" in md
    assert "[^1]" in md and "[^2]" in md


def test_run_writes_file_to_reports_dir():
    q = Query(text="런 테스트")
    report = synthesizer.run(q, [_doc("X")], use_llm=False)
    path = Path(report.markdown_path)
    assert path.exists()
    body = path.read_text(encoding="utf-8")
    assert "런 테스트" in body
    assert report.query_id == q.id
    assert report.doc_ids == [docs_id for docs_id in [_doc("X").id]] or len(report.doc_ids) == 1


def test_slug_drops_special_chars():
    assert synthesizer._slug("LLM/Agent 평가!  benchmark") == "llmagent-평가-benchmark"

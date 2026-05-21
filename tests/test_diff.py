from agents import diff
from agents.models import Document, Query, Report, Source
from storage import db


def _seed(query_text: str, urls: list[str]) -> str:
    q = Query(text=query_text)
    db.save_query(q)
    docs = []
    for url in urls:
        d = Document(query_id=q.id, source=Source(type="paper", url=url))
        d.metadata.title = url.rsplit("/", 1)[-1]
        docs.append(d)
    db.save_documents(docs)
    db.save_report(Report(query_id=q.id, markdown_path=f"reports/{q.id}.md", doc_ids=[d.id for d in docs]))
    return q.id


def test_diff_returns_none_if_only_one_report():
    db.init()
    _seed("주제", ["https://x/a"])
    assert diff.generate("주제", "주제") is None


def test_diff_lists_added_and_removed():
    db.init()
    _seed("주제", ["https://x/a", "https://x/b"])
    _seed("주제", ["https://x/b", "https://x/c"])
    out = diff.generate("주제", "주제")
    assert out and out.exists()
    body = out.read_text(encoding="utf-8")
    assert "신규 (1)" in body
    assert "사라짐 (1)" in body
    assert "https://x/c" in body
    assert "https://x/a" in body

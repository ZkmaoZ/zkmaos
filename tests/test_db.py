from agents.models import Document, Query, Report, Source
from storage import db


def test_init_and_save_roundtrip():
    db.init()
    q = Query(text="db test")
    db.save_query(q)

    d = Document(query_id=q.id, source=Source(type="paper", url="https://x"))
    d.metadata.title = "T"
    d.content.summary = "S"
    db.save_documents([d])

    r = Report(query_id=q.id, markdown_path="reports/x.md", doc_ids=[d.id])
    db.save_report(r)

    with db.connect() as c:
        assert c.execute("SELECT COUNT(*) FROM queries").fetchone()[0] == 1
        assert c.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
        assert c.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 1
        title = c.execute(
            "SELECT json_extract(metadata_json, '$.title') FROM documents"
        ).fetchone()[0]
        assert title == "T"

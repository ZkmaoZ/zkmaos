from agents.models import Citation, Credibility, Document, Query, Source


def test_query_defaults():
    q = Query(text="x")
    assert q.id and q.created_at
    assert "paper" in q.domains and "news" in q.domains
    assert q.depth == "standard"


def test_document_minimum():
    d = Document(source=Source(type="paper", url="https://arxiv.org/abs/1"))
    assert d.id and d.source.fetched_at
    assert d.credibility.score == 0.0
    assert d.metadata.title == ""


def test_document_roundtrip_json():
    d = Document(
        source=Source(type="news", url="https://x"),
        citations=[Citation(text="hello")],
        credibility=Credibility(score=0.7, factors={"r": 1.0}),
    )
    data = d.model_dump()
    assert Document(**data).credibility.score == 0.7

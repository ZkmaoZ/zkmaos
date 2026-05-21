from agents.models import Document, Source
from tools import sources


def test_dedupe_removes_url_variants():
    docs = [
        Document(source=Source(type="paper", url="https://x.com/p?ref=a")),
        Document(source=Source(type="paper", url="https://x.com/p#frag")),
        Document(source=Source(type="paper", url="https://x.com/p/")),
        Document(source=Source(type="paper", url="https://x.com/q")),
    ]
    out = sources._dedupe(docs)
    assert len(out) == 2


def test_search_all_swallows_adapter_errors(monkeypatch):
    def boom(query, limit=5):
        raise RuntimeError("network down")

    monkeypatch.setitem(sources.SEARCH_BY_DOMAIN, "paper", [boom])
    out = sources.search_all("anything", ["paper"], limit=2)
    assert out == []

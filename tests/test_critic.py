from datetime import datetime

from agents import critic
from agents.models import Document, Source


def _doc(*, year: int | None, source_type: str = "paper") -> Document:
    d = Document(source=Source(type=source_type, url="https://x"))
    d.metadata.year = year
    return d


def test_rule_score_recent_paper_high():
    d = _doc(year=datetime.now().year)
    docs = critic.run([d], use_llm=False)
    s = docs[0].credibility
    assert s.score > 0.7
    assert s.factors["recency"] == 1.0
    assert s.factors["peer_reviewed"] == 1.0


def test_rule_score_old_news_low():
    d = _doc(year=2000, source_type="news")
    docs = critic.run([d], use_llm=False)
    assert docs[0].credibility.score < 0.5


def test_kept_excludes_low_scores():
    docs = critic.run(
        [_doc(year=datetime.now().year), _doc(year=1990, source_type="web")],
        use_llm=False,
    )
    kept = critic.kept(docs)
    assert len(kept) == 1
    assert kept[0].metadata.year == datetime.now().year

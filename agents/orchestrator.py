"""Orchestrator — researcher → critic → synthesizer 체인 + 벡터 인덱싱 + diff."""
from __future__ import annotations

from agents import critic, diff, researcher, synthesizer
from agents.models import Query, Report
from agents.synthesizer import _slug
from storage import db, vectors


def run(query_text: str, *, per_domain: int = 5, use_llm: bool = True) -> Report:
    query = Query(text=query_text)
    db.init()
    vectors.init()
    db.save_query(query)

    print(f"[orchestrator] researching: {query.text}")
    docs = researcher.run(query, per_domain=per_domain, enrich=use_llm)
    print(f"[orchestrator] collected {len(docs)} docs")

    docs = critic.run(docs, use_llm=use_llm)
    kept = critic.kept(docs)
    print(f"[orchestrator] {len(kept)}/{len(docs)} passed critic")

    db.save_documents(docs)
    for d in kept:
        vectors.upsert(d.id, d.source.url, d.metadata.title, d.content.summary)

    report = synthesizer.run(query, kept, use_llm=use_llm)
    db.save_report(report)
    print(f"[orchestrator] report: {report.markdown_path}")

    diff_path = diff.generate(query.text, _slug(query.text))
    if diff_path:
        print(f"[orchestrator] diff vs previous: {diff_path}")

    return report

"""직전 동일 주제 보고서와의 차분.

같은 주제(slug 기준) 의 최신 두 보고서를 비교해, 새/사라진/유지된 문서를 알려준다.
출력은 reports/diffs/<slug>-<date>.md 로 저장.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from storage import db

DIFF_DIR = Path(__file__).resolve().parent.parent / "reports" / "diffs"


def _two_latest_for_query(query_text: str) -> list[tuple[str, str, str]]:
    """같은 쿼리 텍스트의 최근 보고서 2개를 (query_id, markdown_path, generated_at) 로 반환."""
    with db.connect() as c:
        rows = c.execute(
            """SELECT q.id, r.markdown_path, r.generated_at
                 FROM reports r JOIN queries q ON q.id = r.query_id
                WHERE q.text = ?
                ORDER BY r.generated_at DESC
                LIMIT 2""",
            (query_text,),
        ).fetchall()
    return rows


def _doc_set(query_id: str) -> dict[str, tuple[str, str]]:
    """query_id 의 문서들을 {url: (id, title)} 로."""
    with db.connect() as c:
        rows = c.execute(
            """SELECT id, url, json_extract(metadata_json,'$.title') AS title
                 FROM documents
                WHERE query_id = ? AND exclude_reason = ''""",
            (query_id,),
        ).fetchall()
    return {url: (doc_id, title or "") for doc_id, url, title in rows}


def generate(query_text: str, slug: str) -> Path | None:
    rows = _two_latest_for_query(query_text)
    if len(rows) < 2:
        return None
    (curr_qid, curr_md, curr_at), (prev_qid, prev_md, prev_at) = rows
    curr = _doc_set(curr_qid)
    prev = _doc_set(prev_qid)

    added = [(u, *curr[u]) for u in curr.keys() - prev.keys()]
    removed = [(u, *prev[u]) for u in prev.keys() - curr.keys()]
    kept = curr.keys() & prev.keys()

    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    out = DIFF_DIR / f"{slug}-{date.today()}.md"

    lines = [
        f"# {query_text} — 변경 사항",
        f"이전: {prev_at}  →  현재: {curr_at}",
        f"이전 보고서: `{prev_md}`",
        f"현재 보고서: `{curr_md}`",
        "",
        f"## 신규 ({len(added)})",
    ]
    for url, _id, title in added:
        lines.append(f"- [{title or url}]({url})")
    lines.append(f"\n## 사라짐 ({len(removed)})")
    for url, _id, title in removed:
        lines.append(f"- [{title or url}]({url})")
    lines.append(f"\n## 유지 ({len(kept)})")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out

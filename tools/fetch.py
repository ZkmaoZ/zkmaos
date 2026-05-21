"""URL → 본문 추출. trafilatura 가 있으면 사용하고, 없으면 단순 텍스트."""
from __future__ import annotations

import re
from pathlib import Path

import httpx

UA = {"User-Agent": "zkmaos-research-agent/0.1"}
TIMEOUT = httpx.Timeout(20.0, connect=10.0)


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_text(url: str, max_chars: int = 8000) -> str:
    try:
        r = httpx.get(url, headers=UA, timeout=TIMEOUT, follow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        return f"[fetch failed: {e}]"

    body = r.text
    try:
        import trafilatura  # type: ignore

        extracted = trafilatura.extract(body, include_comments=False)
        if extracted:
            return extracted[:max_chars]
    except Exception:
        pass
    return _strip_html(body)[:max_chars]


def save_raw(doc_id: str, text: str, base: Path) -> str:
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{doc_id}.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)

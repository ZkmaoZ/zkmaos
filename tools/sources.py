"""도메인별 검색 어댑터.

무인증으로 호출 가능한 공개 API를 우선 사용한다.
- arXiv: http://export.arxiv.org/api/query
- Semantic Scholar Graph API: https://api.semanticscholar.org/graph/v1
"""
from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET

import httpx

from agents.models import Document, Metadata, Source

UA = {"User-Agent": "zkmaos-research-agent/0.1 (+https://github.com/ZkmaoZ/zkmaos)"}
TIMEOUT = httpx.Timeout(15.0, connect=10.0)


def arxiv_search(query: str, limit: int = 5) -> list[Document]:
    """arXiv API 검색. 인증 불필요."""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
    }
    r = httpx.get(
        "http://export.arxiv.org/api/query",
        params=params,
        headers=UA,
        timeout=TIMEOUT,
    )
    r.raise_for_status()

    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(r.text)
    docs: list[Document] = []
    for entry in root.findall("a:entry", ns):
        url = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
        title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
        published = (entry.findtext("a:published", default="", namespaces=ns) or "").strip()
        year = int(published[:4]) if published[:4].isdigit() else None
        authors = [
            (a.findtext("a:name", default="", namespaces=ns) or "").strip()
            for a in entry.findall("a:author", ns)
        ]
        docs.append(
            Document(
                source=Source(type="paper", url=url),
                metadata=Metadata(
                    title=title, authors=authors, year=year, venue="arXiv"
                ),
                content={"summary": summary[:1200], "key_claims": []},
            )
        )
    return docs


def semantic_scholar_search(query: str, limit: int = 5) -> list[Document]:
    """Semantic Scholar Graph API. 키 있으면 더 높은 레이트리밋."""
    headers = dict(UA)
    if key := os.getenv("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = key

    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,authors,venue,url,externalIds",
    }
    r = httpx.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params=params,
        headers=headers,
        timeout=TIMEOUT,
    )
    if r.status_code == 429:
        return []
    r.raise_for_status()
    data = r.json().get("data", [])
    docs: list[Document] = []
    for p in data:
        url = p.get("url") or ""
        if not url and (doi := (p.get("externalIds") or {}).get("DOI")):
            url = f"https://doi.org/{doi}"
        if not url:
            continue
        docs.append(
            Document(
                source=Source(type="paper", url=url),
                metadata=Metadata(
                    title=p.get("title") or "",
                    authors=[a.get("name", "") for a in (p.get("authors") or [])],
                    year=p.get("year"),
                    venue=p.get("venue") or "Semantic Scholar",
                ),
                content={"summary": (p.get("abstract") or "")[:1200], "key_claims": []},
            )
        )
    return docs


def hn_search(query: str, limit: int = 5) -> list[Document]:
    """HackerNews(Algolia) — 기술 동향 무인증 검색."""
    r = httpx.get(
        "https://hn.algolia.com/api/v1/search",
        params={"query": query, "tags": "story", "hitsPerPage": limit},
        headers=UA,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    docs: list[Document] = []
    for hit in r.json().get("hits", []):
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        title = hit.get("title") or ""
        created = hit.get("created_at") or ""
        year = int(created[:4]) if created[:4].isdigit() else None
        docs.append(
            Document(
                source=Source(type="news", url=url),
                metadata=Metadata(title=title, year=year, venue="HackerNews"),
            )
        )
    return docs


def patent_search(query: str, limit: int = 5) -> list[Document]:
    """Google Patents 결과는 무인증 스크래핑이 약관 위반 가능성이 있어 placeholder.
    실서비스에서는 PatentsView(USPTO), KIPRIS 같은 공개 API로 대체할 것.
    """
    return []


SEARCH_BY_DOMAIN = {
    "paper": [arxiv_search, semantic_scholar_search],
    "news": [hn_search],
    "market": [],
    "patent": [patent_search],
}


def _dedupe(docs: list[Document]) -> list[Document]:
    seen: set[str] = set()
    out: list[Document] = []
    for d in docs:
        key = re.sub(r"[#?].*$", "", d.source.url.lower()).rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def search_all(query: str, domains: list[str], limit: int = 5) -> list[Document]:
    """도메인 전반 병렬-아닌 순차 호출. MVP는 단순함 우선."""
    collected: list[Document] = []
    for domain in domains:
        for fn in SEARCH_BY_DOMAIN.get(domain, []):
            try:
                collected.extend(fn(query, limit=limit))
            except Exception as e:
                print(f"[search] {fn.__name__} failed: {e}")
    return _dedupe(collected)

# 연구조사 자동화 에이전트 — 시스템 설계

## 1. 목표
- 자연어 주제 입력 → 신뢰 가능한 출처 기반 보고서 자동 생성
- 학술/기술/시장/특허 4개 도메인 동시 커버
- 정기 실행으로 변화 추적 (모니터링)

## 2. 아키텍처

```
[User Query]
     │
     ▼
Orchestrator ──┬─► Search Agent     (WebSearch / arXiv / Scholar / Patents)
               ├─► Source Agent     (URL/PDF Fetch, 본문 추출, 캐싱)
               ├─► Extract Agent    (요약, 인용, 통계 추출 → JSON)
               └─► Critic Agent     (신뢰도/편향/최신성 평가)
                         │
                         ▼
                  Synthesis Agent   (Markdown 보고서 + 각주)
                         │
                         ▼
                  reports/*.md
```

각 에이전트는 **단일 책임 + 최소 도구 권한** 원칙을 따른다.

| Agent | 허용 도구 |
|---|---|
| Orchestrator | Task(서브에이전트 호출), Read, Write |
| Search | WebSearch, arxiv_search, scholar_search, patent_search |
| Source | WebFetch, pdf_fetch, store_doc |
| Extract | Read, llm_structured_output |
| Critic | Read, llm_evaluate |
| Synthesis | Read, Write |

## 3. 표준 데이터 스키마 (`Document`)

```json
{
  "id": "uuid",
  "query_id": "uuid",
  "source": {
    "type": "paper | web | news | patent | report",
    "url": "https://...",
    "fetched_at": "2026-05-21T09:00:00Z"
  },
  "metadata": {
    "title": "...",
    "authors": ["..."],
    "year": 2025,
    "venue": "NeurIPS",
    "lang": "en"
  },
  "content": {
    "raw_path": "storage/raw/<id>.txt",
    "summary": "3-5 문장",
    "key_claims": ["...", "..."]
  },
  "citations": [{"text": "...", "page": 12, "anchor": "section-3"}],
  "credibility": {
    "score": 0.0,
    "factors": {"peer_reviewed": true, "recency": 0.9, "source_authority": 0.8}
  },
  "tags": ["llm", "agent", "benchmark"]
}
```

## 4. 도메인별 검색 전략

| 도메인 | 1차 소스 | 2차 소스 |
|---|---|---|
| 학술 | arXiv API, Semantic Scholar | Google Scholar (SerpAPI) |
| 기술 동향 | HackerNews, 주요 블로그 RSS | WebSearch |
| 시장·산업 | Statista, 기업 IR, 협회 리포트 | WebSearch + PDF |
| 특허·법률 | Google Patents, KIPRIS, 법령정보 | WebSearch |

## 5. 품질 게이트

Synthesis 전에 Critic이 다음을 검사하고 통과 못 한 문서는 보고서에서 제외:
- 발행일 ≤ 3년 (도메인에 따라 가변)
- URL 해시 중복 제거
- 동일 주장 충돌 시 다수결 + 충돌 리스트로 별도 표기
- 출처 없는 LLM 추정 진술 금지 (모든 주장 → citation 필요)

## 6. 보고서 템플릿

```
# {주제} — 리서치 브리프
생성일: {date}  |  쿼리: {query}  |  문서 수: {n}

## TL;DR
- (3-5 bullet)

## 핵심 발견
### 1) {finding}
... [^1]

## 동향 비교 (옵션)
| 항목 | A | B |

## 충돌·이견
- ...

## 출처
[^1]: {Author, Year, Title, URL}
```

## 7. 정기 모니터링

- `.claude/commands/research.md` 슬래시 커맨드로 주제 등록
- `/loop 7d /research "<topic>"` 로 매주 실행
- 직전 결과와 diff 생성 → `reports/diffs/` 저장

## 8. 도입 스킬 매핑

| Phase | 스킬 |
|---|---|
| 초기 설정 | `/init`, `/update-config`, `/session-start-hook` |
| 개발 | `/claude-api`, `/verify`, `/simplify` |
| 운영 | `/loop`, `/fewer-permission-prompts`, `/run` |

## 9. 로드맵

- **Phase 1 (1주)**: 본 스캐폴딩, MVP Orchestrator + Search + Synthesis
- **Phase 2 (2주)**: Source/Extract/Critic 분리, SQLite 영속화
- **Phase 3 (2주)**: 벡터 검색(Chroma), 보고서 diff, 정기 실행
- **Phase 4**: GitHub Actions 연동, PR/Issue 자동 게시

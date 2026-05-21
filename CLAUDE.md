# zkmaos — Research Automation Agent

연구조사를 자동화하는 멀티 에이전트 시스템입니다. Orchestrator가 작업을 분해해
Search / Source / Extract / Critic / Synthesis 서브에이전트에 위임하고, 결과를
표준 스키마로 저장한 뒤 Markdown 보고서로 합성합니다.

## 런타임
- Python 3.11+
- Claude Agent SDK (`anthropic`)
- 기본 모델: `claude-opus-4-7` (오케스트레이션), `claude-sonnet-4-6` (서브태스크)

## 디렉터리
```
agents/        # Orchestrator + 서브에이전트 구현
tools/         # WebSearch/Fetch, PDF 파서, 인용 추출 등 도구
storage/       # SQLite + 벡터 저장소 인터페이스
reports/       # 생성된 보고서 (Markdown/PDF)
config/        # 도메인별 소스 목록, 보고서 템플릿
docs/          # 설계 문서
.claude/       # subagent · slash command 정의
```

## 핵심 워크플로
1. `python -m agents.run "주제"` 로 단발 리서치 실행
2. `/loop 1w python -m agents.run "주제"` 로 주간 모니터링
3. 결과물은 `reports/YYYY-MM-DD-<slug>.md` 로 저장

## 도메인 커버리지
학술(arXiv/Semantic Scholar), 기술 뉴스, 시장·산업 보고서, 특허·법률.

## 환경 변수
- `ANTHROPIC_API_KEY` (필수)
- `SEMANTIC_SCHOLAR_API_KEY`, `SERPAPI_KEY` (선택, 도메인별)

## 표준 데이터 스키마
`docs/schema.md` 참고. 모든 서브에이전트는 동일 JSON 스키마로 데이터를 주고받음.

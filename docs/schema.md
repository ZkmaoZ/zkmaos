# 표준 데이터 스키마

모든 에이전트 간 데이터 교환은 아래 JSON 스키마를 따른다.

## Query
```json
{
  "id": "uuid",
  "text": "조사 주제 (자연어)",
  "domains": ["paper", "news", "market", "patent"],
  "lang": ["ko", "en"],
  "depth": "shallow | standard | deep",
  "created_at": "ISO8601"
}
```

## Document
`docs/research-agent-design.md` §3 참조.

## Report
```json
{
  "query_id": "uuid",
  "generated_at": "ISO8601",
  "doc_ids": ["..."],
  "sections": {
    "tldr": ["..."],
    "findings": [{"title": "...", "body": "...", "citations": ["doc_id#anchor"]}],
    "conflicts": [],
    "open_questions": []
  },
  "markdown_path": "reports/2026-05-21-llm-agents.md"
}
```

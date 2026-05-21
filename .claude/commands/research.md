---
description: 주제 하나에 대한 전체 리서치 파이프라인 실행 (researcher → critic → synthesizer)
argument-hint: <조사 주제>
---

다음 주제에 대해 리서치 파이프라인을 실행하세요: **$ARGUMENTS**

수행 단계:
1. `researcher` 서브에이전트를 호출해 Document 배열을 수집
2. `critic` 서브에이전트로 검증 → exclude 대상 제외
3. `synthesizer` 서브에이전트로 `reports/` 에 Markdown 보고서 생성
4. 생성된 보고서 경로와 핵심 요약 3줄을 사용자에게 보고

각 단계는 순차적으로 진행하며, 단계별 결과를 다음 에이전트의 입력으로 전달하세요.

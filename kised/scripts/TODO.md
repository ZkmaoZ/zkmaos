# scripts/ TODO

다음 세션에서 붙일 검사기. 지금은 자리만 비워둠 — 실제 스캔 파일이
1개 이상 누적된 뒤에 그 포맷에 맞춰 짠다.

## 1. graduation_lint (졸업 게이트)

- 입력: `scans/*.md` 또는 임의 마크다운.
- 검사: 정량값(숫자 + 단위) 옆에 `[매체 — 스캔, 미재검증]` 또는
  `[미확인]` 태그가 없으면 fail.
- 용도: 외부 브리프로 승격 시 pre-commit 또는 수동 lint.

## 2. structure_check (반증·무행동 누락 검사)

- 입력: `scans/YYYY-MM-DD.md`.
- 검사: 다음 헤더가 모두 존재하는지 — 머리말 스탬프 / 반증 후보 /
  무행동 옵션 / 한계.
- 미존재 시 fail.

## 3. (선택) axes_guard

- `axes.yml`의 `locked: true` 상태에서 PR이 axes.yml을 수정하면 경고.
- 누적 일관성 보호용.

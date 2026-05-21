#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$ROOT/scans/TEMPLATE.md"
TODAY="$(date +%Y-%m-%d)"
OUT="$ROOT/scans/${TODAY}.md"

if [ -e "$OUT" ]; then
  echo "이미 존재: $OUT"
  exit 1
fi

sed "s/YYYY-MM-DD/${TODAY}/g" "$TEMPLATE" > "$OUT"
echo "생성: $OUT"

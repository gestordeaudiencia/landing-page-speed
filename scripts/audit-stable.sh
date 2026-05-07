#!/usr/bin/env bash
# Run lighthouse 3x per URL, report median score.
# Usage: ./audit-stable.sh <url1> [url2] ...
set -euo pipefail

NPM_BIN="$(npm config get prefix 2>/dev/null)/bin"
[ -d "$NPM_BIN" ] && export PATH="$NPM_BIN:$PATH"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <url1> [url2] ..."
  exit 1
fi

RUNS="${RUNS:-3}"

mkdir -p /tmp/lh-stable
: > /tmp/lh-stable/results.txt

for url in "$@"; do
  slug=$(basename "${url%/}")
  scores=()
  echo "→ $slug ($RUNS runs)"
  for i in $(seq 1 $RUNS); do
    out=/tmp/lh-stable/${slug}-${i}.json
    lighthouse "$url" \
      --only-categories=performance \
      --form-factor=mobile \
      --throttling-method=devtools \
      --output=json \
      --output-path="$out" \
      --quiet \
      --chrome-flags="--headless=new --no-sandbox" 2>/dev/null
    sc=$(jq -r '.categories.performance.score' "$out")
    pct=$(awk "BEGIN{printf \"%d\", ${sc:-0} * 100}")
    fcp=$(jq -r '.audits["first-contentful-paint"].numericValue' "$out")
    lcp=$(jq -r '.audits["largest-contentful-paint"].numericValue' "$out")
    tbt=$(jq -r '.audits["total-blocking-time"].numericValue' "$out")
    cls=$(jq -r '.audits["cumulative-layout-shift"].numericValue' "$out")
    echo "  run$i: score=$pct  FCP=${fcp%.*}ms  LCP=${lcp%.*}ms  TBT=${tbt%.*}ms  CLS=$cls"
    scores+=("$pct")
  done
  sorted=($(printf '%s\n' "${scores[@]}" | sort -n))
  median=${sorted[$((RUNS/2))]}
  echo "  ═ median: $median/100"
  echo "$slug median=$median runs=${scores[*]}" >> /tmp/lh-stable/results.txt
done

echo ""
echo "═══ Final medians ═══"
cat /tmp/lh-stable/results.txt

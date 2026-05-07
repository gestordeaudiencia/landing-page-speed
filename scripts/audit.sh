#!/usr/bin/env bash
# Audit pages with Lighthouse local + devtools throttling.
# Usage: ./audit.sh <url1> [url2] [url3] ...
# Defaults to no URLs — must pass at least one.
set -euo pipefail

# Auto-detect npm-global bin (works for any user)
NPM_BIN="$(npm config get prefix 2>/dev/null)/bin"
[ -d "$NPM_BIN" ] && export PATH="$NPM_BIN:$PATH"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <url1> [url2] [url3] ..."
  exit 1
fi

mkdir -p /tmp/lh-audit
SUMMARY=/tmp/lh-audit/summary.txt
: > "$SUMMARY"

for url in "$@"; do
  slug=$(basename "${url%/}")
  out=/tmp/lh-audit/${slug}.json
  echo "──────────────────────────────────────"
  echo "→ $url"
  echo "──────────────────────────────────────"

  lighthouse "$url" \
    --only-categories=performance \
    --form-factor=mobile \
    --throttling-method=devtools \
    --output=json \
    --output-path="$out" \
    --quiet \
    --chrome-flags="--headless=new --no-sandbox" 2>/dev/null || {
      echo "  Lighthouse error — page may have NO_LCP issue (Lantern bug). Try --throttling-method=devtools manually."
      continue
    }

  score=$(jq -r '.categories.performance.score' "$out")
  score_pct=$(awk "BEGIN{printf \"%d\", ${score:-0} * 100}")

  fcp=$(jq -r '.audits["first-contentful-paint"].displayValue // "N/A"' "$out")
  lcp=$(jq -r '.audits["largest-contentful-paint"].displayValue // "N/A"' "$out")
  tbt=$(jq -r '.audits["total-blocking-time"].displayValue // "N/A"' "$out")
  cls=$(jq -r '.audits["cumulative-layout-shift"].displayValue // "N/A"' "$out")
  si=$(jq -r '.audits["speed-index"].displayValue // "N/A"' "$out")

  {
    echo ""
    echo "═══ $slug ═══"
    echo "  Score: $score_pct/100"
    echo "  FCP:   $fcp"
    echo "  LCP:   $lcp"
    echo "  TBT:   $tbt"
    echo "  CLS:   $cls"
    echo "  SI:    $si"
    echo ""
    echo "  Top opportunities (savings ms):"
    jq -r '
      .audits
      | to_entries
      | map(select(.value.details.overallSavingsMs != null and .value.details.overallSavingsMs > 50))
      | sort_by(-.value.details.overallSavingsMs)
      | .[0:5]
      | .[]
      | "    \(.value.details.overallSavingsMs)ms  \(.key)"
    ' "$out"
    echo ""
    echo "  Failed audits (score<0.9):"
    jq -r '
      .audits
      | to_entries
      | map(select(.value.score != null and .value.score < 0.9))
      | sort_by(.value.score)
      | .[0:8]
      | .[]
      | "    \(.value.score)  \(.key) — \(.value.title)"
    ' "$out"
  } | tee -a "$SUMMARY"
done

echo ""
echo "═══════════════════════════════════════"
echo "Summary saved: $SUMMARY"
echo "JSONs: /tmp/lh-audit/"

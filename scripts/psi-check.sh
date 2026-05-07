#!/usr/bin/env bash
# Run PageSpeed Insights API and report top issues for a URL.
# Usage: ./psi-check.sh <url> [strategy=mobile|desktop]
# Optional: export PSI_API_KEY="AIza..." (free at console.cloud.google.com)
# Without key: rate-limited to ~100/day. With key: ~25k/day.

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <url> [strategy]"
  exit 1
fi

URL="$1"
STRATEGY="${2:-mobile}"
API="https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed"
OUT=/tmp/psi-result.json

QS="url=${URL}&strategy=${STRATEGY}&category=performance"
if [ -n "${PSI_API_KEY:-}" ]; then
  QS="${QS}&key=${PSI_API_KEY}"
fi

echo "→ Testing $URL ($STRATEGY)"
echo "  fetching PSI ..."

curl -sS "${API}?${QS}" -o "$OUT"

if jq -e '.error' "$OUT" >/dev/null 2>&1; then
  echo "ERROR:"
  jq '.error' "$OUT"
  exit 1
fi

SCORE=$(jq -r '.lighthouseResult.categories.performance.score' "$OUT")
SCORE_PCT=$(awk "BEGIN{printf \"%d\", ${SCORE:-0} * 100}")

echo ""
echo "═══ Performance Score: $SCORE_PCT/100 ═══"
echo ""

jq -r '
  .lighthouseResult.audits as $a |
  [
    {k:"FCP",v:$a["first-contentful-paint"].displayValue,s:$a["first-contentful-paint"].score},
    {k:"LCP",v:$a["largest-contentful-paint"].displayValue,s:$a["largest-contentful-paint"].score},
    {k:"TBT",v:$a["total-blocking-time"].displayValue,s:$a["total-blocking-time"].score},
    {k:"CLS",v:$a["cumulative-layout-shift"].displayValue,s:$a["cumulative-layout-shift"].score},
    {k:"SI", v:$a["speed-index"].displayValue,s:$a["speed-index"].score}
  ]
  | .[]
  | "  \(.k)\t\(.v // "N/A")\t(score: \(.s // "n/a"))"
' "$OUT"

echo ""
echo "Note: PSI score 0 with NO_LCP error is a Lantern simulator bug for pages with"
echo "deferred players. Use Lighthouse local (audit.sh) for true measurement."
echo ""
echo "═══ Top opportunities (sorted by potential savings ms) ═══"
jq -r '
  .lighthouseResult.audits
  | to_entries
  | map(select(.value.details.overallSavingsMs != null and .value.details.overallSavingsMs > 0))
  | sort_by(-.value.details.overallSavingsMs)
  | .[0:8]
  | .[]
  | "  \(.value.details.overallSavingsMs)ms\t\(.key)\t— \(.value.title)"
' "$OUT"

echo ""
echo "Full JSON: $OUT"

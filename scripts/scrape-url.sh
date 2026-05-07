#!/usr/bin/env bash
# Scrape a live URL: fetch HTML + critical assets to /tmp/scraped-<timestamp>/.
# Usage: ./scrape-url.sh <url>
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <url>"
  exit 1
fi

URL="$1"
TS=$(date +%s)
OUT="/tmp/scraped-${TS}"
mkdir -p "$OUT/assets"

echo "→ Scraping $URL"
echo "  output: $OUT"
echo ""

# 1. Fetch HTML with a real browser UA (avoid bot blocks)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -sSL -A "$UA" "$URL" -o "$OUT/index.html" -w "HTTP %{http_code} | size %{size_download}b | time %{time_total}s\n"

if [ ! -s "$OUT/index.html" ]; then
  echo "ERROR: empty HTML returned"
  exit 1
fi

LEN=$(wc -c < "$OUT/index.html")
echo "  HTML size: $LEN bytes"
echo ""

# 2. Check if SPA (mostly empty body)
BODY_SIZE=$(grep -oE '<body[^>]*>.*</body>' "$OUT/index.html" | wc -c || echo 0)
if [ "$BODY_SIZE" -lt 1000 ]; then
  echo "  ⚠ HTML body looks empty/SPA — basic scrape may not capture content."
  echo "  Try headless: google-chrome --headless --disable-gpu --dump-dom \"$URL\" > $OUT/index.html"
  echo ""
fi

# 3. Extract image/CSS/JS URLs (just for inspection — assets stay external for now)
echo "→ External resources referenced:"
echo ""
echo "  Images:"
grep -oE 'src="[^"]+\.(jpg|jpeg|png|webp|avif|gif|svg)"' "$OUT/index.html" 2>/dev/null \
  | sort -u | head -10 | sed 's/^/    /'

echo ""
echo "  CSS:"
grep -oE '<link[^>]+href="[^"]+\.css[^"]*"' "$OUT/index.html" 2>/dev/null \
  | sort -u | head -10 | sed 's/^/    /'

echo ""
echo "  JS:"
grep -oE '<script[^>]+src="[^"]+\.js[^"]*"' "$OUT/index.html" 2>/dev/null \
  | sort -u | head -10 | sed 's/^/    /'

echo ""
echo "  Forms:"
grep -oE '<form[^>]+action="[^"]+"' "$OUT/index.html" 2>/dev/null \
  | sort -u | head -5 | sed 's/^/    /'

echo ""
echo "═══════════════════════════════════════"
echo "Done. Scraped HTML: $OUT/index.html"
echo ""
echo "Next step: detect stack"
echo "  python3 \$(dirname \$0)/detect-stack.py $OUT/index.html"

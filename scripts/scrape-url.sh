#!/usr/bin/env bash
# Scrape a live URL: fetch HTML + critical assets to /tmp/scraped-<timestamp>/.
# Auto-detects SPA pages and falls back to headless Chrome rendering.
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

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# 1. Fetch HTML with curl + browser UA
echo "  [1/3] curl with browser UA ..."
curl -sSL -A "$UA" "$URL" -o "$OUT/index.html" -w "    HTTP %{http_code} | size %{size_download}b | time %{time_total}s\n"

if [ ! -s "$OUT/index.html" ]; then
  echo "ERROR: empty response"
  exit 1
fi

HTML_SIZE=$(wc -c < "$OUT/index.html" | tr -d ' ')
echo "    HTML: $HTML_SIZE bytes"
echo ""

# 2. Detect SPA — check if body is mostly empty or has known SPA root markers
echo "  [2/3] checking if SPA ..."
SPA=0
# Body content size heuristic
BODY_TEXT=$(python3 -c "
import re,sys
with open('$OUT/index.html') as f: html=f.read()
m=re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL|re.IGNORECASE)
if m:
    body=m.group(1)
    # Strip script/style content
    body=re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL|re.IGNORECASE)
    body=re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL|re.IGNORECASE)
    body=re.sub(r'<[^>]+>', '', body)
    body=body.strip()
    print(len(body))
else:
    print(0)
" 2>/dev/null || echo 0)

# Known SPA framework markers in HTML
if grep -qE '<div id="(root|app|__next|__nuxt|svelte)"[^>]*></div>' "$OUT/index.html"; then
  SPA=1
  echo "    ⚠ SPA marker found (empty root div)"
elif grep -qE 'window\.__NUXT__|window\.__INITIAL_STATE__|<noscript>You need to enable JavaScript' "$OUT/index.html"; then
  SPA=1
  echo "    ⚠ SPA framework detected"
elif [ "$BODY_TEXT" -lt 200 ]; then
  SPA=1
  echo "    ⚠ Body text content very small ($BODY_TEXT chars) — likely SPA"
else
  echo "    ✓ Looks server-rendered ($BODY_TEXT chars of body text)"
fi

# 3. If SPA, attempt headless render
if [ "$SPA" = "1" ]; then
  echo ""
  echo "  [3/3] attempting headless render ..."
  CHROME=""
  for c in google-chrome chrome chromium "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then
      CHROME="$c"
      break
    fi
  done

  if [ -n "$CHROME" ]; then
    echo "    using: $CHROME"
    "$CHROME" --headless=new --disable-gpu --no-sandbox \
      --virtual-time-budget=10000 \
      --user-agent="$UA" \
      --dump-dom "$URL" > "$OUT/index-headless.html" 2>/dev/null || true

    if [ -s "$OUT/index-headless.html" ]; then
      HEADLESS_SIZE=$(wc -c < "$OUT/index-headless.html" | tr -d ' ')
      if [ "$HEADLESS_SIZE" -gt "$HTML_SIZE" ]; then
        mv "$OUT/index.html" "$OUT/index-curl.html"
        mv "$OUT/index-headless.html" "$OUT/index.html"
        echo "    ✓ headless got $HEADLESS_SIZE bytes (curl was $HTML_SIZE) — using headless"
      else
        rm -f "$OUT/index-headless.html"
        echo "    headless not larger — keeping curl version"
      fi
    else
      echo "    headless render failed — keeping curl version"
      rm -f "$OUT/index-headless.html"
    fi
  else
    echo "    ⚠ Chrome not found. To headless-scrape SPA pages, install Google Chrome or"
    echo "      run manually: google-chrome --headless --dump-dom \"$URL\" > $OUT/index.html"
  fi
else
  echo ""
  echo "  [3/3] skipping headless (server-rendered)"
fi

# 4. Inspect resources
echo ""
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
echo "  JS (top 10):"
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
echo "Next: detect stack"
echo "  python3 \$(dirname \$0)/detect-stack.py $OUT/index.html"

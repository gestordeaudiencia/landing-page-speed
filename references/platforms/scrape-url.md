# Scrape from live URL

When user gives only URL (no file, no platform info).

## Quick scrape

```bash
./scripts/scrape-url.sh https://example.com/path
```

Outputs to `/tmp/scraped-<timestamp>/`:
- `index.html` — fully-rendered HTML
- `assets/` — images, CSS, JS referenced by URL

## What scrape captures

- Server-rendered HTML (works for GHL, WP, ClickFunnels, Webflow, raw HTML)
- Inline `<style>`, `<script>` content
- External resources via absolute URLs (kept as URLs)

## What scrape DOESN'T capture (limits)

- **Client-rendered SPAs** (React/Vue/Angular without SSR) — scrape gets empty `<div id="root">`. Use a headless-browser scrape instead (puppeteer/playwright).
- **Pages behind login** — scrape returns login page. Need cookie/auth.
- **Lazy-loaded content** below scroll — only initial viewport content captured.
- **JavaScript-rendered popups, modals** — only initial DOM state captured.

## Headless scrape (for SPAs)

If basic scrape returns empty `<body>`, use puppeteer:

```bash
npx puppeteer-launch <<EOF
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com', { waitUntil: 'networkidle2' });
  const html = await page.content();
  console.log(html);
  await browser.close();
})();
EOF
```

Or use Chrome DevTools Protocol via Bash:
```bash
google-chrome --headless --disable-gpu --dump-dom https://example.com > scraped.html
```

## Trust check before deploying

Before deploying scraped content:
1. **Visual diff:** open scraped HTML in browser, compare against live URL screenshot
2. **Asset paths:** if scraped HTML references `/wp-content/uploads/...`, those paths break on new host. Either rewrite to absolute URLs OR download assets locally
3. **Forms:** verify form actions are absolute URLs (not relative `/submit`)
4. **License:** if scraping someone else's page (not yours), consider IP/copyright

## Asset rewriting

If scrape captures HTML with relative paths:
```html
<img src="/uploads/hero.jpg">
<link rel="stylesheet" href="/styles.css">
```

These break on new domain. Two options:

**Option A — rewrite to absolute (simplest):**
```python
body = body.replace('src="/uploads/', 'src="https://oldsite.com/uploads/')
body = body.replace('href="/styles', 'href="https://oldsite.com/styles')
```

**Option B — download + serve locally (more work, faster, no 3rd party dependency):**
```bash
# scrape-url.sh does this automatically — downloads referenced assets to /tmp/scraped-X/assets/
```

Then update HTML to use local paths. Build to `public/` of Astro project.

## When scraped is ready

Hand off to standard workflow:
1. `python3 scripts/detect-stack.py /tmp/scraped-X/index.html`
2. `python3 scripts/build-from-html.py /tmp/scraped-X/index.html public/optimized/index.html config.json`
3. Build + deploy

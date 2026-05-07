# Universal Performance Principles

These apply to ANY landing page on ANY platform. Apply in priority order. Re-audit after each.

## Priority order (highest impact first)

### 1. Defer heavy 3rd-party JS until first interaction

**Targets:** video players, chat widgets, CRM popups, A/B test SDKs, heavy analytics.

**Pattern:** wrap script injection in event listeners + timeout fallback.

```js
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    // ... your 3rd party initialization
  }
  ["scroll","touchstart","mousemove","click","keydown"].forEach(function(ev){
    window.addEventListener(ev,load,{once:true,passive:true});
  });
  setTimeout(load,15000);  // fallback for non-interactive bots/Lighthouse
})();
```

**Impact:** -1 to -2s LCP, -200ms TBT.

### 2. Pre-style body in `<head>`

**Why:** scripts that mutate body styles after paint cause CLS.

```html
<style>
html,body{background:#fff;margin:0;padding:0;overflow-x:hidden}
</style>
```

Replace bg color with page's actual color. Add other defaults the page sets via JS later.

### 3. Drop or async-load fonts

**Best:** if size-adjusted fallback exists (Next.js Inter Fallback, etc), drop external Google Fonts entirely. Visual ~95% identical.

**Acceptable:** async load via media trick:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=...">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=..." media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=..."></noscript>
```

### 4. Defer pixels and analytics

Meta Pixel, GTM, GA4, TikTok, etc — all defer 1.5s after `load`:
```js
window.addEventListener('load', function() {
  setTimeout(loadTrackingScript, 1500);
});
```

Tradeoff: lose ~2-5% PageView events from sessions <1s. Acceptable for performance.

### 5. Add poster image for LCP detection

If using deferred video player, add an `<img>` placeholder so Lighthouse Lantern detects LCP candidate. Inline as data URI for zero extra requests.

### 6. content-visibility:auto on below-fold

```css
body > section:nth-of-type(n+4) {
  content-visibility: auto;
  contain-intrinsic-size: auto 1000px;
}
```

Tune `nth-of-type` so first 3-5 sections render instantly.

### 7. Cache headers

For Cloudflare Pages (`_headers` file):
```
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable

/_next/image*
  Cache-Control: public, max-age=2592000

/images/*
  Cache-Control: public, max-age=2592000

/{slug}/*
  Cache-Control: public, max-age=300, must-revalidate
```

Other hosts: equivalent config (Netlify _headers, Vercel vercel.json, nginx.conf, etc).

### 8. Preconnect critical 3rd-party origins

Limit to 2-3 origins (TCP+TLS handshake budget):
```html
<link rel="preconnect" href="https://CRITICAL_CDN" crossorigin>
<link rel="dns-prefetch" href="https://NON_CRITICAL_DOMAIN">
```

### 9. Preload above-fold hero image

```html
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">
```

Don't preload images that aren't above the fold.

### 10. Disable non-composited animations

Animations on `box-shadow`, `background`, `filter`, layout properties trigger paints/reflows.

```css
.btn { animation: none !important; }  /* kills box-shadow pulse */
.floating-logo { animation: none !important; }
.hero-mockup { animation: none !important; }
```

Composited animations (transform, opacity) are fine — keep those.

### 11. Strip render-blocking JS

Look for `<script src>` without `async` or `defer` in `<head>` — those block parser. Add `defer`:
```html
<script src="..." defer></script>
```

Inline scripts in `<head>` that do DOM manipulation: move to bottom of `<body>` or wrap in `setTimeout(..., 0)`.

### 12. Compress and use right format

Brotli compression: most CDNs auto-apply. Verify via:
```bash
curl -sI -H "Accept-Encoding: br" https://your-page/ | grep -i content-encoding
```

Should show `br`. If not, configure host.

Image formats: AVIF > WebP > JPEG/PNG. CF Image Resizing or `<picture>` with `<source type="image/avif">` fallback.

## Variance / measurement

**Lighthouse local with `--throttling-method=devtools`** is the most reliable score (matches Chrome real measurement).

**Lighthouse Lantern (PSI default) bug**: pages with deferred players often throw `NO_LCP` even when real LCP is fine. Wait for CrUX data (~2 weeks) → PSI uses field metrics, bug irrelevant.

**Run-to-run variance ±3-5 points.** Always run 3+ times, use **median**.

## Score targets

| Score | Meaning |
|---|---|
| 95-100 | Top tier. Fast for any user. |
| 90-94 | Acceptable. Push to 95+ if effort allows. |
| 70-89 | Below ideal. Real users on 4G see lag. |
| <70 | Bad. Major issues. |

## Common ceiling causes (when stuck below 95)

- 3rd party JS (player, pixel, GTM) — can't shrink
- 3rd party images on slow CDNs (no caching control) — proxy via CF Image Resizing if budget allows
- Legacy JS shipped by vendors — no control
- Server response time on cold edge — first-hit ~150-300ms, warms after
- Heavy custom CSS (Tailwind utilities not purged) — run PurgeCSS

When you hit ceiling, document remaining issues. User decides if acceptable.

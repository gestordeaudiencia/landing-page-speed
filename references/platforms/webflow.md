# Webflow

## Detection markers

- `<html data-wf-page="..." data-wf-site="...">`
- `<script src="https://d3e54v103j8qbb.cloudfront.net/.../webflow.*.js">`
- CSS class names like `w-button`, `w-form`, `w-container`
- `<meta name="generator" content="Webflow">`

## Native export

Webflow has native HTML export (Workspace plan $19/mo+):
1. Webflow dashboard → site settings → Export Code
2. Download ZIP with `index.html`, `css/`, `js/`, `images/`
3. Pass `index.html` to `scripts/build-from-html.py`

If user is on free plan (no export), use scrape:
```bash
./scripts/scrape-url.sh https://yoursite.webflow.io/
```

## Webflow-specific gotchas

### `webflow.js` (~200KB)

Adds: form validation, dropdowns, sliders, IX2 (interactions), navbar scrolling.

**For static migration:**
- If page has Webflow IX2 animations: needs `webflow.js`. Defer load via interaction trigger.
- If page is plain hero+text+CTA: strip `webflow.js` entirely. Saves ~200KB.

### IX2 Interactions

Webflow's animation system. Adds JS that runs on scroll/hover/etc.

**Performance:** scroll-triggered animations can hurt CLS and TBT.

**Migration option:**
- Keep IX2 (load `webflow.js`) — accept perf cost
- Strip IX2 — replace key animations with CSS-only equivalents

CSS replacements:
```css
.fade-in {
  opacity: 0;
  animation: fadeIn 0.6s ease-out forwards;
}
@keyframes fadeIn { to { opacity: 1; } }
```

Or `animation-timeline: view()` (modern browsers — scroll-driven CSS animations).

### Webflow Forms

Forms POST to `https://webflow.com/api/v1/form/...`. Cross-origin works.

If migrating to subdomain, form still submits to Webflow. Test that emails come through.

For CRM integration: Webflow → form submission → Zapier → CRM (or use form action override to direct CRM webhook).

### Webflow CMS pages

If page uses `{{wf {... CMS items ...}}}` placeholders, page is dynamic. Static export captures one rendered version.

If you migrate, you lose CMS dynamic update. For VSL/landing page (single static version), fine.

### Style sheet scoping

Webflow scopes all CSS by site → no global conflicts. Their CSS uses class prefixes like `cc-`, `_`, etc. Keep all CSS to preserve visual.

## Common page types

| Type | Migrate? |
|---|---|
| Marketing landing | Yes — Path B (static export + optimize) |
| VSL page | Yes — biggest perf gain |
| Portfolio/blog | Maybe — Webflow's own hosting is decent |
| eCommerce | No — keep on Webflow Ecommerce |
| Membership site | No — Webflow handles auth |

## Optimization expectations

Webflow exported HTML typically scores ~75-85 on PageSpeed already (Webflow ships clean code). After our optimizations: 95+.

Mostly we just defer the player + pixel + content-visibility. Less work than GHL or WP migrations.

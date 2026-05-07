# Elementor + WordPress

WordPress + Elementor is the heaviest common stack. Pages typically score 40-70 on PageSpeed before optimization.

## Three migration paths (pick one)

### Path A — Keep on WP, optimize there (less work)

Don't migrate. Install plugins:
- **WP Rocket** ($59/yr) or **LiteSpeed Cache** (free) — caching, minify, defer
- **Perfmatters** ($25/yr) — disable unused features, defer scripts
- **ShortPixel** or **Smush** — image optimization
- **Asset CleanUp** — remove unused JS/CSS per page

Setup typically gets WP from 50 → 80 score. Worth doing if user wants WP.

### Path B — Static HTML export (recommended for VSLs)

Export page as static HTML, host on CDN. WordPress becomes editor only.

**Tools:**
- **Simply Static** plugin (free + pro $99) — exports static HTML
- **WP2Static** (free) — same
- **Strattic** (paid SaaS) — managed solution

**How:**
1. Build page in WordPress/Elementor as usual
2. Run static export plugin
3. Get ZIP of `index.html` + `wp-content/uploads/` images + `wp-includes/` CSS/JS
4. Pass `index.html` to `scripts/build-from-html.py` for further optimization
5. Deploy to CF Pages

**Result:** ~95+ Lighthouse score after optimization.

### Path C — Full rebuild on Astro (most work, best result)

For pages where speed is critical (paid ads, VSLs), rebuild from scratch on Astro using the WP page as visual reference. Skip WordPress entirely.

## Scrape live URL (faster than export)

If page already live:
```bash
./scripts/scrape-url.sh https://yoursite.com/page
```

Gets fully-rendered HTML.

## Elementor-specific gotchas

### Multiple `<link>` to elementor CSS files

WordPress + Elementor loads:
- `wp-content/uploads/elementor/css/post-XXX.css` (Elementor styles)
- `wp-includes/css/dist/block-library/style.min.css` (Gutenberg blocks)
- `wp-content/themes/THEME/style.css` (theme)
- Plus 5-10 plugin CSS files

**Optimization:** combine into single inline `<style>` block. Use PurgeCSS to remove unused rules (typically 60-80% removable).

### jQuery + Elementor frontend JS

WordPress ships ~150KB of legacy JS (jquery, jquery-migrate, elementor-frontend, etc).

**For static export:** if page doesn't need interactive Elementor widgets (no popups, sliders, etc), strip ALL Elementor JS. Page renders perfectly without it.

If page needs sliders: keep just `elementor-frontend.min.js`, strip the rest. Or replace slider with native CSS scroll-snap.

### Inline `<style id="elementor-post-XXX-...">` with custom CSS

Elementor injects per-section styles inline. Keep these — they're already optimized.

### Lazy load images

Elementor sets `loading="lazy"` automatically on most images. For above-fold hero, change to `loading="eager"` and add `fetchpriority="high"`.

## Common ad pages from WP

| Type | Performance work |
|---|---|
| OptinMonster popup pages | Strip OptinMonster JS, keep only relevant popup |
| Thrive Themes / Architect | Heavy — usually full rebuild |
| Divi pages | Heavy CSS + JS — Path C recommended |
| Generic Elementor + Astra theme | Path B works well |
| WooCommerce product page | Don't migrate — keep on WP for cart |

## Pixel/checkout integration

WP plugins typically add Meta Pixel via:
- PixelYourSite plugin
- Manual `<head>` script
- GTM container

After scrape, find pixel ID and apply defer pattern from `references/pixels.md`.

Checkout: usually external link to Hotmart/Eduzz/Kiwify. Just keep the link.

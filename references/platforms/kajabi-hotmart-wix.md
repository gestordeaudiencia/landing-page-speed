# Kajabi / Hotmart Pages / Wix / Other SaaS Builders

These all share similar patterns: SaaS-hosted, limited HTML access, heavy JS framework.

## Kajabi

**Detection:** `<script src="https://assets.kajabi-cdn.com/...">`, class names like `kjbi-*`

**Export:** No native export. Must scrape:
```bash
./scripts/scrape-url.sh https://yoursite.kajabi.com/page
```

**Tradeoff:** Kajabi handles auth + courses + payments. If you ONLY want to migrate marketing pages (sales/landing), scrape + migrate. Keep Kajabi for the rest.

**JS to strip:** Kajabi frontend JS (~150KB). Most landing pages don't need it.

## Hotmart Pages (page builder)

**Detection:** URL `*.hotmart.com/page/...` or `*.pay.hotmart.com`

**Export:** Hotmart Pages doesn't allow export. Scrape:
```bash
./scripts/scrape-url.sh https://yourdomain.com
```

**Migration tip:** Hotmart Pages is just a landing page. Conversion happens on Hotmart Checkout (different URL). Easy migration — page is mostly static + checkout link.

## Wix

**Detection:** `<meta name="generator" content="Wix.com Website Builder">`, `<div id="SITE_ROOT">`

**Export:** Wix has paid plan with HTML export, but quality is poor (dynamic JS rendering). **Best:** scrape live URL.

**Heavy:** Wix loads ~500KB+ of JS framework even for static pages. Scraping captures rendered HTML, then we strip all Wix JS.

**Result after migration:** ~300-500KB → ~50KB. Score 30-60 → 95+.

## Kartra

**Detection:** `pages.kartra.com` URLs, class names `kt-*`

**Export:** None. Scrape only.

**Migration tip:** Similar to Kajabi — keep Kartra for funnels/products, migrate just landing pages.

## Cartpanda

**Detection:** `*.cartpanda.com` URLs

Same pattern: scrape + migrate.

## Generic strategy for any SaaS builder

1. **Scrape** the live URL (basic scrape works for SaaS — they SSR)
2. **Strip platform JS** — usually 80-95% of JS can go
3. **Keep CSS** — usually fine, just inlined platform styles
4. **Keep external links** — checkout, forms, etc
5. **Re-deploy** to CF Pages on subdomain
6. **Test forms** still submit (cross-origin works for most providers)

## What you typically lose migrating off SaaS

- Native A/B testing (use GrowthBook on CF instead, or Cloudflare Workers)
- Built-in popup builder (rebuild popup as plain HTML/CSS)
- Native analytics dashboard (use GA4 or Plausible)
- Visual editor (must edit HTML directly via Claude Code)

## What you keep

- All conversion features (checkout, forms, pixel tracking)
- SEO (might improve)
- Speed (massive improvement)
- Cost ($0 hosting vs $20-300/mo SaaS)

## Decision matrix

| Use case | Migrate? |
|---|---|
| Paid ad VSL | YES — speed = CVR |
| SEO landing | YES |
| Affiliate/promo page | YES |
| Course sales page | YES (keep platform for delivery) |
| Membership area | NO |
| eCommerce | NO |
| Blog | YES (use Astro Content Collections) |

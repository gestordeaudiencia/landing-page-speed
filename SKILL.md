---
name: landing-page-speed
description: Use when user wants to migrate a slow landing page (from GoHighLevel/GHL, ClickFunnels, Kajabi, Hotmart, Webflow, or any platform-hosted page) to Cloudflare Pages with maximum performance. Also use when user asks to "fazer LP rápida", "otimizar landing page", "subir VSL no Cloudflare", "deixar página rápida", "PageSpeed no talo", or wants to audit a page with Lighthouse/PSI. Handles HTML wrapping, vturb/wistia/vimeo player deferral, pixel deferral, font self-hosting, cache headers, custom domain via Astro + Cloudflare Pages, and full audit feedback loop.
---

# Landing Page Speed

Migrate slow landing pages → Cloudflare Pages + Astro with max perf (Lighthouse 95+).

## When this skill applies

Triggers:
- User has slow LP on GHL / ClickFunnels / Kajabi / Hotmart / Webflow / Wix
- Wants to subir LP nova rápida
- Wants Lighthouse / PSI score alto
- Diz "otimiza essa página", "deixa rápida", "VSL com performance"
- Tem HTML do GHL e quer hospedar fora

## Required prerequisites

Before starting, confirm with user:
1. Cloudflare account (free tier works)
2. Cloudflare API token with Pages + Workers Scripts edit perms
3. Domain already on Cloudflare nameservers OR access to DNS at registrar
4. HTML of current landing page (export from GHL Custom Code embed, or scrape)
5. Subdomain plan (e.g., `lp.dominio.com`) — easier than touching root

## Workflow (high level)

1. **Init Astro project** — `npm create astro@latest <name> -- --template minimal`
2. **Place HTML** — wrap GHL embed in proper `<!doctype>` shell (see `references/build-template.md`)
3. **Apply optimizations** — defer vturb to interaction, drop Google Fonts, pre-style body, cache headers, preconnect (see `references/optimization-playbook.md`)
4. **Add poster img** — for Lighthouse Lantern LCP detection (see `references/snippets.md`)
5. **Deploy** — `wrangler pages deploy`
6. **Custom domain** — CF API + CNAME at registrar
7. **Audit loop** — run `scripts/audit-stable.sh` + iterate until ≥95 median

## Optimization priority order

Apply in this order. After each, re-audit. Stop when target reached.

1. **Defer player (vturb/wistia/vimeo)** until first user interaction (`scroll`, `touchstart`, `click`, `mousemove`, `keydown`) OR 7s timeout. Biggest single win (~2s LCP).
2. **Drop Google Fonts CSS** if local Inter Fallback exists. Use system or self-hosted woff2.
3. **Pre-style body** in `<head>` (margin/padding/bg) to prevent script-driven CLS.
4. **Add poster `<img>`** in player container so Lighthouse Lantern detects LCP candidate.
5. **Preconnect critical origins** (player CDN, image CDN, pixel).
6. **Preload hero image** with `fetchpriority="high"`.
7. **Cache headers** via `_headers` for `/_next/static/*` (1y immutable), images (30d).
8. **Disable non-composited animations** (box-shadow pulse, float on absolute logos) if PageSpeed flags them.
9. **Defer pixel Meta** to `load + 1.5s` via `setTimeout`.
10. **Strip GHL container-escape JS** in standalone (irrelevant outside GHL parent).

## Auditing

Three tools available:
- `scripts/audit.sh <url>` — single Lighthouse run mobile devtools throttling
- `scripts/audit-stable.sh <url1> <url2> ...` — 3 runs each, reports median
- `scripts/psi-check.sh <url>` — PSI API (needs key, see below)

**Important:** PSI Lantern (simulator) often throws `NO_LCP` for pages with deferred players, even when Lighthouse local detects LCP fine. This is a known PSI bug. Once page has CrUX data (real-user metrics), PSI uses field data and bug becomes irrelevant. Don't chase Lantern errors — use Lighthouse local with `--throttling-method=devtools` as truth.

## PSI API key

Optional. Get free at console.cloud.google.com → APIs → PageSpeed Insights API → Credentials → API key. Set in env: `export PSI_API_KEY=AIza...`. Free tier ~25k/day with key, ~100/day without.

## Honest tradeoffs

User must accept:
- Player loads on first interaction (user sees static poster until they scroll/touch)
- If using "drop Google Fonts" option: text renders in size-adjusted Arial fallback (95% visually same as Inter, no real difference)
- Pulse/float animations disabled (visual polish loss for perf)
- `animate-up` fade-in disabled (elements appear directly)

If user rejects these tradeoffs, document which they want to keep. Score will be lower but visual identical.

## Workflow checklist

When user requests optimization, follow:

1. [ ] Confirm prerequisites (CF account, domain, HTML source)
2. [ ] Read `references/optimization-playbook.md`
3. [ ] Read `references/snippets.md` for the patterns
4. [ ] Init Astro project at agreed path
5. [ ] Wrap HTML using `scripts/build-from-html.py` template
6. [ ] Run `scripts/audit-stable.sh` for baseline
7. [ ] Apply optimizations one at a time in priority order
8. [ ] Re-audit after each change
9. [ ] Stop at score ≥95 OR user says "good enough"
10. [ ] Set up custom domain if not done
11. [ ] Document tradeoffs taken in a final summary

## Reference files

- `references/optimization-playbook.md` — every optimization explained
- `references/snippets.md` — code patterns (defer vturb, pixel, etc)
- `references/deploy-cf.md` — Cloudflare Pages + custom domain via wrangler/API
- `scripts/build-from-html.py` — parameterized HTML wrapper template
- `scripts/audit.sh` — single-run Lighthouse audit
- `scripts/audit-stable.sh` — 3-run median audit
- `scripts/psi-check.sh` — PSI API caller

## When NOT to use

- User wants to keep page on GHL/ClickFunnels/etc (just optimize there) — different skill
- User wants full landing page DESIGN from scratch — use `build-page` or `lead-magnet` skills
- User wants to write COPY for the page — use `copywriting` skill

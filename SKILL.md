---
name: landing-page-speed
description: Use when user wants to optimize the loading speed of any landing page from any platform — GoHighLevel (GHL), Elementor + WordPress, ClickFunnels, Hotmart Pages, Kajabi, Webflow, Wix, Kartra, Cartpanda, raw HTML, scraped pages, or any URL. Also use when user asks to "fazer LP rápida", "otimizar landing page", "subir VSL no Cloudflare", "deixar página rápida", "PageSpeed no talo", "/optimize", "performance da minha página", "minha página tá lenta", "score Lighthouse", "Core Web Vitals". Handles auto-detection of stack (player/pixel/checkout/platform), universal performance optimizations (defer heavy JS, async fonts, content-visibility, cache headers), and deploys to user's chosen host (Cloudflare Pages default, also supports Netlify/Vercel/GitHub Pages).
---

# Landing Page Speed Optimizer

**One job:** make any landing page from any platform load as fast as physically possible. Target Lighthouse 95+, real LCP <1s.

## When invoked: follow this step-by-step

This is an **interactive workflow**. Walk the user through it, ask questions, don't assume.

### Step 0 — Greet + ask source

Tell the user (in their language — match what they wrote):

> "Vou otimizar tua landing page. Pra começar, me diz como tu tens a página hoje:
>
> 1. **URL ao vivo** — me passa o link, eu baixo o HTML
> 2. **Arquivo HTML** local — me dá o caminho
> 3. **Plataforma** específica (GHL, WordPress/Elementor, ClickFunnels, etc) — me diz qual e como exportar"

Wait for their answer. Don't proceed without it.

### Step 1 — Get the HTML

Based on their answer:

**If URL:** use `scripts/scrape-url.sh <url>` to download HTML + critical assets.

**If file path:** read the file.

**If platform name:** read `references/platforms/<platform>.md` for export instructions, then ask user to do the export and paste the file path.

### Step 2 — Auto-detect stack

Run `python3 scripts/detect-stack.py <html-file>`. It detects:
- **Player**: vturb, wistia, vimeo, youtube, jwplayer, panda, html5 video
- **Pixel**: Meta (fbq), GTM, GA4 (gtag), TikTok, Pinterest, LinkedIn
- **Checkout**: Hotmart, Eduzz, Kiwify, LastLink, Stripe, PayPal, custom links
- **Platform fingerprints**: GHL classes, Elementor IDs, ClickFunnels markers, Webflow generator, etc
- **Fonts**: Google Fonts, Adobe Fonts, self-hosted

Show user the detection result. Ask:
> "Detectei isso: [list]. Tá certo? Algo que faltou?"

### Step 3 — Confirm tradeoffs

Tell user explicitly what you'll do that affects UX/visual:

- Player carrega no primeiro scroll/touch (poster aparece antes)
- Pixel dispara 1.5s depois do load (perde ~2-5% sessões muito curtas)
- Animações não-essenciais desligadas (pulse CTA, float)
- Fontes: drop Google Fonts se houver fallback size-adjusted, OU async load
- Sections abaixo da dobra: `content-visibility:auto` (raríssima possibilidade de flash em scroll rápido)

Ask: "Tudo bem com isso? Se algum item NÃO topar, me fala."

Document any rejected tradeoffs — apply only the rest.

### Step 4 — Pick deploy target

Ask user where to host:
- **Cloudflare Pages** (default, recommended — free, edge global, custom domain via API)
- **Netlify**
- **Vercel**
- **GitHub Pages**
- **Self-hosted** (just generate optimized HTML + assets, user uploads)

Read corresponding `references/hosts/<host>.md` for setup steps.

### Step 5 — Build optimized version

Use `scripts/build-from-html.py <input> <output> <config.json>` with config that matches detected stack + user-confirmed tradeoffs.

Output: standalone optimized HTML + assets.

### Step 6 — Deploy

Per host guide. For CF Pages:
```bash
wrangler pages deploy dist --project-name <name> --commit-dirty=true --branch main
```

### Step 7 — Custom domain (optional)

If user has domain, walk through CNAME setup. Subdomain recommended (e.g., `lp.dominio.com`) to avoid touching root.

### Step 8 — Audit loop

Run `scripts/audit-stable.sh <url>` (3 runs, median).

Show user the score. If <95:
1. Read `references/universal-principles.md` priority order
2. Pick next optimization not yet applied
3. Apply via `build-from-html.py` re-run with updated config
4. Re-deploy
5. Re-audit

Stop at score ≥95 OR after 5 iterations OR user says "good enough".

### Step 9 — Final summary

Report:
- Before/after scores
- Which optimizations applied
- Tradeoffs taken
- URL ready to use
- Domain verification status (Meta/Google Ads inherit from root domain — usually no re-verification needed)

## Reference files (load when relevant)

| File | When to read |
|---|---|
| `references/universal-principles.md` | Always — core rules |
| `references/players.md` | When stack has any video player |
| `references/pixels.md` | When tracking pixel detected |
| `references/checkouts.md` | When checkout link found |
| `references/platforms/<name>.md` | When user names a platform |
| `references/hosts/<name>.md` | When user picks a host |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/detect-stack.py <html>` | Auto-detect tech stack |
| `scripts/scrape-url.sh <url>` | Download HTML + assets from live URL |
| `scripts/build-from-html.py <in> <out> <cfg.json>` | Apply optimizations |
| `scripts/audit.sh <url1> [url2]...` | Single Lighthouse audit |
| `scripts/audit-stable.sh <url1> [url2]...` | 3-run median |
| `scripts/psi-check.sh <url>` | PSI API call |

## Prerequisites

User needs (one-time):
```bash
npm install -g lighthouse wrangler
```

Optional:
- `PSI_API_KEY` for PSI API (free at console.cloud.google.com)
- `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` for CF Pages deploy

## Honest expectations

- Lighthouse 95+ achievable for most pages
- PSI Lantern simulator may show NO_LCP for pages with deferred players — known bug, resolves once page accumulates CrUX field data (~2 weeks of real traffic)
- Real-world LCP <1s typical
- Target Core Web Vitals all "Good": LCP, CLS, INP

## When NOT to use this skill

- User wants page DESIGN from scratch — use `build-page` or `lead-magnet`
- User wants to write COPY — use `copywriting`
- User wants to keep page on platform (just optimize there) — different skill
- User has SPA/React app — use frontend-design skill (different optimization patterns)

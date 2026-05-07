# landing-page-speed

Universal Claude Code skill — optimize the loading speed of **any landing page from any platform**.

Works with: GoHighLevel (GHL), Elementor + WordPress, ClickFunnels, Hotmart Pages, Kajabi, Webflow, Wix, Kartra, Cartpanda, raw HTML, scraped URLs, anything else.

Targets: **Lighthouse 95+**, real LCP <1s, Core Web Vitals all "Good".

## What it does

When invoked, walks the user through an interactive workflow:

1. **Asks how the page exists** (URL / HTML file / platform name)
2. **Auto-detects stack** — player, pixel, checkout, platform, fonts
3. **Confirms tradeoffs** — what visual/UX changes user accepts
4. **Picks deploy target** — Cloudflare Pages, Netlify, Vercel, GitHub Pages, self-hosted
5. **Builds optimized version** — applies all relevant performance patterns
6. **Deploys**
7. **Sets up custom domain** (optional)
8. **Audits in feedback loop** — Lighthouse local + PSI API, iterates until score ≥95

## Install

```bash
git clone https://github.com/gestordeaudiencia/landing-page-speed.git ~/.claude/skills/landing-page-speed
npm install -g lighthouse wrangler
```

## Invoke

In Claude Code, any of these triggers the skill:
- `/optimize` (if you have it as a slash command)
- "otimiza minha landing page"
- "deixa essa página rápida"
- "PageSpeed no talo"
- "score Lighthouse"
- Just paste a URL and ask "make this fast"

The skill auto-triggers on description match.

## Coverage

### Platforms
- GoHighLevel (GHL) Custom Code embeds
- WordPress + Elementor (export, scrape, or rebuild)
- ClickFunnels
- Webflow (native export or scrape)
- Wix, Kajabi, Hotmart Pages, Kartra, Cartpanda
- Raw HTML / hand-coded
- Live URL scrape (any platform)

### Video players
- vturb / converteai (defer + poster swap)
- Wistia (defer + placeholder)
- Vimeo (click-to-play + thumbnail)
- YouTube (click-to-play + hqdefault thumb)
- JWPlayer (defer init)
- Panda Video (click-to-play)
- Native HTML5 video

### Tracking pixels
- Meta Pixel (Facebook)
- Google Tag Manager (GTM)
- Google Analytics 4 (GA4 / gtag)
- TikTok Pixel
- Pinterest Tag
- LinkedIn Insight
- Hotjar
- Microsoft Clarity

### Checkouts
- Hotmart, Eduzz, Kiwify, LastLink
- Stripe, PayPal, MercadoPago
- Cartpanda, ClickBank, Doppus, PerfectPay
- Monetizze, Braip
- Custom links

### Hosts
- Cloudflare Pages (recommended, default)
- Netlify
- Vercel
- GitHub Pages
- Self-hosted (nginx, S3, R2, VPS)

## Files

```
SKILL.md                       — interactive workflow + manifest
README.md                      — this file
references/
  universal-principles.md      — core perf rules (always apply)
  optimization-playbook.md     — every optimization in priority order
  players.md                   — defer pattern per player type
  pixels.md                    — defer pattern per tracking script
  checkouts.md                 — checkout integration patterns
  snippets.md                  — copy-paste code patterns
  platforms/
    ghl.md
    elementor-wp.md
    clickfunnels.md
    webflow.md
    raw-html.md
    scrape-url.md
    kajabi-hotmart-wix.md
  hosts/
    cloudflare-pages.md
    netlify.md
    vercel.md
    github-pages.md
    self-hosted.md
scripts/
  detect-stack.py              — auto-detect tech stack
  scrape-url.sh                — fetch HTML + assets from URL
  build-from-html.py           — wrap embed → optimized standalone
  audit.sh                     — single Lighthouse run
  audit-stable.sh              — 3-run median
  psi-check.sh                 — PSI API
```

## Real-world results

Tested on 3 GHL VSL pages (`cloudcoding.com.br/comece2`, etc):

**Before** (GHL native):
- HTML transfer: 265 KB
- TTFB: 400-500ms
- LCP: 2-4s
- Lighthouse mobile: ~25-50

**After** (this skill, Cloudflare Pages):
- HTML transfer: 21 KB (-92%)
- TTFB: 70-120ms (-75%)
- LCP: <1s (-75%)
- Lighthouse mobile: 96-99

## Honest expectations

- 95+ Lighthouse achievable for most pages
- Real-world LCP <1s typical
- Some optimizations have visual/UX tradeoffs — skill confirms each with user
- PSI Lantern simulator may show NO_LCP for pages with deferred players (known PSI bug, resolves once page accumulates CrUX field data ~2 weeks)
- Lighthouse local with `--throttling-method=devtools` is the most reliable metric

## License

MIT

# landing-page-speed

Claude Code skill — migrate slow landing pages (GoHighLevel, ClickFunnels, Kajabi, Hotmart, Webflow) to **Cloudflare Pages + Astro** with maximum performance. Targets Lighthouse 95+.

## What it does

- Wraps GHL Custom Code embed HTMLs into standalone `<!doctype>` pages
- Defers video player (vturb / wistia / vimeo / youtube) to first user interaction
- Replaces player with a poster `<img>` so Lighthouse Lantern detects LCP candidate
- Drops blocking Google Fonts (uses size-adjusted Arial fallback)
- Pre-styles body in `<head>` to prevent script-driven CLS
- Adds preconnects + preload + cache headers
- Defers Meta Pixel / GTM 1.5s after `load`
- Strips GHL container-escape JS in standalone context
- Disables non-composited animations
- Audits via Lighthouse local + PSI API in feedback loop

## Result

Real-world reduction: ~265KB → 21KB transfer. TTFB 400ms → 70ms. Lighthouse 25 → 97-99.

## Install

```bash
git clone https://github.com/gestordeaudiencia/landing-page-speed.git ~/.claude/skills/landing-page-speed
```

Then in any Claude Code session:

> "otimiza minha LP do GHL e sobe no Cloudflare"

Skill auto-triggers via description match.

## Dependencies

```bash
npm install -g lighthouse wrangler
```

## CF setup (one-time)

```bash
export CLOUDFLARE_API_TOKEN="cfat_..."
export CLOUDFLARE_ACCOUNT_ID="..."
```

Token perms: Cloudflare Pages Edit + Workers Scripts Edit + Account Settings Read. Get at dash.cloudflare.com → My Profile → API Tokens.

## Files

```
SKILL.md                                  — skill manifest, workflow, when-to-use
references/
  optimization-playbook.md                — every optimization explained, priority order
  snippets.md                             — copy-paste code patterns (vturb defer, pixel, etc)
  deploy-cf.md                            — Astro + Cloudflare Pages + custom domain via API
scripts/
  audit.sh <url> [url...]                 — single Lighthouse run mobile + devtools throttling
  audit-stable.sh <url> [url...]          — 3 runs each, reports median (variance protection)
  psi-check.sh <url> [strategy]           — PSI API call (set PSI_API_KEY env)
  build-from-html.py <in> <out> [cfg]     — wrap GHL embed → standalone with optimizations
```

## Workflow

1. Init Astro project at chosen path
2. Drop GHL HTML at `dist-ghl/variant-X.html`
3. Build via `python3 scripts/build-from-html.py dist-ghl/variant-a.html public/comece2/index.html config.json`
4. Build Astro: `npm run build`
5. Deploy: `wrangler pages deploy dist`
6. Audit: `./scripts/audit-stable.sh https://your-url.pages.dev/comece2/`
7. Apply optimizations from playbook in priority order
8. Re-audit + iterate until median ≥95

## License

MIT

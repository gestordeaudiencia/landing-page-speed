# GitHub Pages

Free, simplest, works for any user with a GitHub account.

## Limits

- 1GB site size
- 100GB bandwidth/mo soft limit
- Public repo (or paid GH Pages on private repos via GitHub Pro)
- No server-side functions
- No edge network — single origin (us-east region)

**Speed:** worse than CF Pages / Netlify / Vercel for global traffic. OK for low-volume or tech audience.

## Setup

```bash
cd your-project
git init
gh repo create your-lp --public --source=. --remote=origin --push
```

Enable Pages:
1. github.com/user/your-lp → Settings → Pages
2. Source: GitHub Actions OR Deploy from a branch
3. If branch: pick `main`, folder `/` or `/docs`

For Astro:
```bash
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm ci && npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: ./dist }
      - uses: actions/deploy-pages@v4
```

## Custom domain

1. Settings → Pages → Custom domain → enter `lp.dominio.com`
2. At registrar, add CNAME: `<user>.github.io`
3. Enable "Enforce HTTPS" (after SSL provisions, ~10 min)

## Cache headers

GitHub Pages doesn't allow custom cache headers. All assets get default `Cache-Control: max-age=600`.

This hurts repeat-visit performance. CF Pages or Netlify better for this.

## When to use

- Tech demos / portfolios
- Open-source project sites
- Free static blogs
- Quick experiments

## When NOT to use

- High-traffic ad pages (no edge network)
- Pages with PII forms (no server-side)
- Sites needing custom redirects/headers

## Migration tip

Even if user picks GitHub Pages, propose CF Pages — same simplicity, much better performance, also free. Only use GH Pages if user has reason (already using GH for everything, hates other clouds, etc).

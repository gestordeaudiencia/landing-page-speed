# Vercel

Free tier: 100GB bandwidth/mo. Built for Next.js but works for any static site.

## Setup (one-time)

```bash
npm install -g vercel
vercel login
```

## Deploy

```bash
cd <project>
npm run build  # generates dist/
vercel --prod --yes
```

First run prompts for project name. Saves to `.vercel/project.json`.

## Configuration via vercel.json

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "headers": [
    {
      "source": "/_next/static/(.*)",
      "headers": [{"key":"Cache-Control","value":"public, max-age=31536000, immutable"}]
    },
    {
      "source": "/images/(.*)",
      "headers": [{"key":"Cache-Control","value":"public, max-age=2592000"}]
    }
  ],
  "redirects": [
    {"source":"/old-path","destination":"/new-path","permanent":true}
  ]
}
```

## Custom domain

Via dashboard:
1. vercel.com/your-project/settings/domains → Add domain
2. Add CNAME at registrar: `cname.vercel-dns.com`
3. SSL auto via Let's Encrypt

Via CLI:
```bash
vercel domains add lp.dominio.com
```

## Edge network

Vercel Edge Network: ~30 PoPs globally. Fast for US/EU, decent for BR.

## Build cache

Vercel caches `node_modules` between builds. First build slow (~2-3 min), subsequent ~30s.

## Brotli + HTTP/3

Auto on all plans.

## Image Optimization

`<Image>` component (Next.js only) auto-optimizes. For static HTML, use Vercel's Image API:
```html
<img src="https://yoursite.com/_vercel/image?url=https://example.com/image.jpg&w=720&q=75">
```

Costs apply on Pro plan ($20/mo).

## Edge Functions / Middleware

Available on Pro+. For most landing pages, not needed.

## Comparison vs CF Pages

| Feature | Vercel | CF Pages |
|---|---|---|
| Free bandwidth | 100GB/mo | unlimited |
| Edge nodes | ~30 | 300+ |
| Build speed | fast (~30s) | similar |
| Native Next.js | ✅ | ✅ |
| Image opt | Pro plan | Paid ($5/mo) |
| For LP/marketing | great | great |

Pick Vercel if: already using for other Next.js apps, want one dashboard.
Pick CF Pages if: want unlimited bandwidth, more edge locations, lower cost at scale.

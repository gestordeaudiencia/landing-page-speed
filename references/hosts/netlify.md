# Netlify

Free tier: 100GB bandwidth/mo, 300 build min/mo. Generous for ad pages.

## Setup (one-time)

```bash
npm install -g netlify-cli
netlify login
```

## Deploy

```bash
cd <project>
npm run build  # generates dist/
netlify deploy --prod --dir=dist --site=<site-name>
```

First deploy without `--site` creates new site, prompts name. Saves config to `.netlify/state.json`.

## Custom domain

Via dashboard:
1. app.netlify.com → site → Domain settings → Add custom domain
2. Netlify shows DNS targets:
   - **A record:** `75.2.60.5` (Netlify's load balancer)
   - **CNAME:** `<site-name>.netlify.app`
3. At your registrar, add CNAME for subdomain:
   ```
   Type: CNAME
   Name: lp
   Value: <site-name>.netlify.app
   ```
4. Netlify auto-provisions SSL via Let's Encrypt (5-15 min)

Via CLI:
```bash
netlify api updateSite --data '{"site_id":"...","custom_domain":"lp.dominio.com"}'
```

## Cache headers

Create `public/_headers`:
```
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable

/images/*
  Cache-Control: public, max-age=2592000

/*.html
  Cache-Control: public, max-age=300, must-revalidate
```

Or `netlify.toml`:
```toml
[[headers]]
  for = "/_next/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/images/*"
  [headers.values]
    Cache-Control = "public, max-age=2592000"
```

## Redirects

For migrating old URLs to new ones, `_redirects` file:
```
/old-page  https://newsite.com/new-page  301
/comece2   /comece2/                     301
```

## Brotli + HTTP/3

Auto on free tier. Verify:
```bash
curl -sI -H "Accept-Encoding: br" https://yoursite/ | grep -i content-encoding
```

## Forms

Netlify Forms (free 100 submissions/mo) — replace `<form>` with:
```html
<form name="contact" netlify>
  <input type="email" name="email" required>
  <button type="submit">Submit</button>
</form>
```

Submissions appear in Netlify dashboard. No backend needed.

## Comparison vs CF Pages

| Feature | Netlify | CF Pages |
|---|---|---|
| Free bandwidth | 100GB/mo | unlimited |
| Build minutes | 300/mo free | 500/mo free |
| Edge nodes | ~30 | 300+ |
| Build deploy time | ~1-3 min | ~30-60s |
| Custom domain SSL | LE auto | Google CA auto |
| Forms | Native (free 100/mo) | None (use Workers) |
| Image optimization | Paid | Paid (Image Resizing $5/mo) |

For Brazilian traffic: CF Pages slightly faster (more edges in BR). For form-heavy sites: Netlify easier.

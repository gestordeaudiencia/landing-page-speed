# Cloudflare Pages Deploy Guide

## One-time setup

### 1. Cloudflare API token

User's path: dash.cloudflare.com → My Profile → API Tokens → Create Token → Custom

Required permissions:
- Account → Cloudflare Pages → Edit
- Account → Workers Scripts → Edit
- Account → Account Settings → Read

Save token + account ID:
```bash
export CLOUDFLARE_API_TOKEN="cfat_..."
export CLOUDFLARE_ACCOUNT_ID="abc123..."
```

### 2. Wrangler CLI

```bash
npm install -g wrangler
wrangler whoami  # validate
```

## Per-project workflow

### Init Astro

```bash
mkdir -p ~/Projects/my-lp && cd ~/Projects/my-lp
npm create astro@latest . -- --template minimal --no-install --no-git --skip-houston --typescript strict
npm install
```

### Add public assets

Drop in `public/`:
- `vsl-poster.svg` (see snippets.md)
- `_headers` (see snippets.md)
- `favicon.ico` (optional)
- LP HTMLs at `public/<slug>/index.html`

### Astro config

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
export default defineConfig({
  output: 'static',
  build: { inlineStylesheets: 'auto' },
});
```

### Build

```bash
npm run build
# Output → dist/
```

### Create Pages project (first time)

```bash
wrangler pages project create my-lp --production-branch main
```

If 500 error from API: check listing — sometimes project was created despite error:
```bash
wrangler pages project list
```

### Deploy

```bash
wrangler pages deploy dist --project-name my-lp --commit-dirty=true --branch main
```

Outputs:
- Production: `https://my-lp.pages.dev`
- This deploy: `https://abc123.my-lp.pages.dev`

## Custom domain

### If domain DNS is on Cloudflare

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects/my-lp/domains" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"lp.dominio.com"}'
```

CF auto-creates CNAME record + provisions SSL via Google CA.

### If domain DNS at registrar (Registro.br, GoDaddy, etc)

1. Run same API call as above
2. CF returns `verification_data.status: pending` + tells you to add CNAME
3. At registrar DNS panel, add:
   - Type: CNAME
   - Name: `lp` (or whatever subdomain)
   - Value: `my-lp.pages.dev`
   - TTL: 3600
4. Wait 5-30 min for propagation
5. CF auto-validates and provisions SSL

### Verify deployment

```bash
# DNS propagation
dig lp.dominio.com +short

# CF domain status
curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects/my-lp/domains/lp.dominio.com" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq '.result.status'

# Live test
curl -sI https://lp.dominio.com/comece2/
```

## Subdomain strategy (recommended for migrations)

Don't touch root `dominio.com` if other funnels live there. Use subdomain like `lp.dominio.com`. Keeps GHL etc intact, allows progressive migration.

After validating new pages perform well, redirect old URLs:
- GHL: URL Redirects → `/comece2` → `https://lp.dominio.com/comece2/`
- Or update CTAs in ads / emails to point to new subdomain directly

## Common errors

**"Project not found"**: project doesn't exist. Create it first.

**"500 Internal Server Error" on project create**: transient. Re-list — project may have been created anyway.

**"NXDOMAIN" on dig**: DNS not propagated. Wait longer. Check CNAME spelling.

**"Initializing" status forever**: CNAME points to wrong target. Verify exact value `<project-name>.pages.dev`.

**SSL cert pending**: takes 5-15 min after DNS resolves. Check back.

## Multiple environments

Use branches:
- `main` → production (https://my-lp.pages.dev)
- `staging` → preview (https://staging.my-lp.pages.dev)

```bash
wrangler pages deploy dist --project-name my-lp --branch staging
```

## Rollback

Each deploy gets unique URL. Promote previous deploy via dashboard:
dash.cloudflare.com → Workers & Pages → my-lp → Deployments → [previous] → Promote

Or re-deploy older `dist/` folder from git history.

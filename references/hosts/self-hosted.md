# Self-hosted (VPS / nginx / S3 / R2)

For users who want full control.

## When to pick this

- User already has VPS/cloud (DigitalOcean, AWS, GCP, etc)
- Need integration with backend on same server
- Want zero 3rd-party dependencies

## nginx static config

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name lp.dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name lp.dominio.com;

    root /var/www/lp;
    index index.html;

    ssl_certificate /etc/letsencrypt/live/lp.dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lp.dominio.com/privkey.pem;

    # Brotli (requires ngx_brotli module)
    brotli on;
    brotli_comp_level 6;
    brotli_types text/html text/css text/javascript application/javascript application/json image/svg+xml;

    # Gzip fallback
    gzip on;
    gzip_comp_level 6;
    gzip_types text/html text/css text/javascript application/javascript application/json image/svg+xml;

    # Cache static assets
    location ~ ^/(_next/static|images|videos|favicon\.ico) {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # HTML: short cache
    location / {
        expires 5m;
        add_header Cache-Control "public, must-revalidate";
        try_files $uri $uri/ $uri.html =404;
    }
}
```

Setup SSL with Let's Encrypt:
```bash
sudo certbot --nginx -d lp.dominio.com
```

## Deploy via rsync

From your local build:
```bash
rsync -avz --delete dist/ user@server:/var/www/lp/
```

## AWS S3 + CloudFront

```bash
aws s3 sync dist/ s3://your-bucket/ --delete
aws cloudfront create-invalidation --distribution-id ABCDEFG --paths "/*"
```

CloudFront config: cache behavior for `*.html` short, `/_next/static/*` 1 year, custom origin = S3.

## Cloudflare R2 + Workers

CF R2 is cheaper than S3 (no egress fee). Combine with Workers for routing:

```js
// worker.js
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let key = url.pathname.replace(/^\//, '');
    if (key === '' || key.endsWith('/')) key += 'index.html';
    const obj = await env.BUCKET.get(key);
    if (!obj) return new Response('Not Found', {status: 404});
    return new Response(obj.body, {
      headers: {
        'Content-Type': obj.httpMetadata.contentType,
        'Cache-Control': key.startsWith('_next/static/') 
          ? 'public, max-age=31536000, immutable' 
          : 'public, max-age=300, must-revalidate'
      }
    });
  }
};
```

Bind R2 bucket in `wrangler.toml`:
```toml
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "lp-bucket"
```

Deploy:
```bash
wrangler r2 object put lp-bucket/index.html --file dist/index.html
wrangler deploy
```

## Performance tuning checklist

For self-hosted:

- [ ] HTTP/2 enabled (or HTTP/3 if available)
- [ ] Brotli compression configured
- [ ] Cache headers set per resource type
- [ ] Static assets served with long cache + immutable
- [ ] HTML served with short cache + must-revalidate
- [ ] HTTPS via Let's Encrypt (auto-renewal cron)
- [ ] CDN in front (Cloudflare proxy free, recommended even for VPS)
- [ ] gzip fallback for older browsers without brotli

## When self-hosted gets ugly

- Cert renewal fails → site goes down
- Server load spike → slow response
- Backups/redundancy not handled → data loss risk
- DDoS protection needed → CF in front anyway

For most users: **CF Pages free** > self-hosted. Pick self-hosted only with specific reason.

# ClickFunnels

## Detection markers

- `<script src="https://cdn.funnelytics.io/script.js">` (FF tracking)
- `<meta name="generator" content="ClickFunnels">`
- URL pattern `*.clickfunnels.com` or custom domain with CF DNS
- `cf-funnel-step-id` data attributes
- jQuery + jquery-ui + Bootstrap loaded

## How to export

ClickFunnels doesn't have native export. Options:

### Option A — Scrape URL

```bash
./scripts/scrape-url.sh https://yourpage.com
```

Gets rendered HTML. ClickFunnels pages are fully server-rendered, scrape captures everything.

### Option B — View source + manual copy

1. Open published page in Chrome
2. Right-click → "View Page Source"
3. Save as `.html`
4. Inline images may use ClickFunnels CDN URLs — keep as-is, they cache fine

## CF-specific gotchas

### Heavy jQuery + jQuery UI bundle

CF pages load ~200KB of jQuery + jQuery UI + Bootstrap. Most isn't needed.

**For migration:** strip all `<script>` tags pointing to ClickFunnels CDN. Keep only what's actually used. If page is just hero + CTA + form, you need ZERO JS from CF.

### CF form actions

CF forms POST to `*.clickfunnels.com/track-form-submission`. After migration:

**Option 1:** keep form pointing to CF endpoint (works cross-domain)
**Option 2:** replace with direct integration to your CRM/email tool (ConvertKit, ActiveCampaign, GHL webhook, etc)

### Funnel step tracking

CF tracks user progress through funnel steps via `cf-funnel-step-id`. After migration, this stops working — but it's just CF's analytics, not conversion-critical.

If you want analytics, replace with GA4 events:
```js
gtag('event','funnel_step_viewed',{step:'optin'});
```

### Sticky bars & timers

CF has built-in scarcity timers and sticky bars. If used:
- **Timer (countdown):** rebuild as native JS
```html
<div id="timer">15:00</div>
<script>
var deadline = Date.now() + 15*60*1000;
setInterval(function(){
  var rem = deadline - Date.now();
  var m = Math.floor(rem/60000);
  var s = Math.floor((rem%60000)/1000);
  document.getElementById('timer').textContent = m+':'+(s<10?'0':'')+s;
}, 1000);
</script>
```
- **Sticky bar:** plain CSS `position:fixed;bottom:0`

## Page types

| CF type | Can migrate? |
|---|---|
| Optin page | Yes, easy |
| VSL / sales page | Yes (best target — speed matters most) |
| Webinar registration | Yes |
| Order form | Maybe — if simple. Complex order forms keep on CF |
| Membership area | No — keep on CF |
| Upsell/downsell | No — funnel logic on CF |

## Migration tip

ClickFunnels charges ~$97/mo. After migrating ad pages to CF Pages (free), you save money + gain speed. Keep CF for funnel logic (one-click upsells, order forms) where speed matters less.

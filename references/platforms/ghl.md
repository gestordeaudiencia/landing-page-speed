# GoHighLevel (GHL)

## How to export HTML

GHL doesn't have native "export site" — but you can get the HTML two ways:

### Option A — Custom Code Embed (cleanest)

If user built page using GHL's HTML/Custom Code element (entire page is one block):
1. GHL Funnel/Site → edit page → click the Custom Code element
2. Copy entire HTML from the editor
3. Paste into a `.html` file locally

Result: HTML fragment starting with `<style>` (no doctype). The `build-from-html.py` script wraps it.

### Option B — Scrape live URL

If page is published and live:
```bash
./scripts/scrape-url.sh https://yourpage.com/path
```

This downloads the rendered HTML + critical assets. GHL serves a wrapper around the custom code — scrape gets everything.

## GHL-specific gotchas

### Container escape script

GHL pages embed user code inside their own DOM wrapper. They include this script to break out:
```js
var b=document.body;
b.style.setProperty('background','...','important');
var el=root.parentElement;
while(el && el!==document.body){
  el.style.setProperty('padding','0','important');
  ...
}
```

**In standalone (after migration):** this script does nothing (no GHL parent wrapper). It just causes a forced reflow on initial load. **Strip it.**

The `build-from-html.py` does this automatically when `kill_ghl_container_escape: true` (default).

### `.animate-up` IntersectionObserver

GHL templates often add fade-in-on-scroll via:
```css
.animate-up{opacity:0;transition:...;transform:translateY(30px)}
.animate-up.visible{opacity:1;transform:translateY(0)}
```
And JS that observes elements + adds `.visible`.

**Problem:** elements start invisible — Lighthouse may have trouble detecting LCP candidates.

**Fix:** override CSS to keep elements visible. Strip the IO setup. The script handles this.

### LeadConnector / stcdn JS

GHL pages embed `stcdn.leadconnectorhq.com/_preview/*.js` — editor JS that does nothing in production.

**Fix:** when using Custom Code Embed (Option A), this is automatically excluded. Scraped pages may have these — strip via:
```python
body = re.sub(r'<script[^>]+stcdn\.leadconnectorhq\.com[^>]+></script>', '', body)
```

## Common GHL page types

| Type | Notes |
|---|---|
| Funnel page (1-step) | Single page in a funnel — typical VSL or sales page |
| Funnel page (2-step) | Hero + form → thanks page |
| Website (multi-page) | Full site with nav |
| Membership page | Behind login — skip optimizing, just keep on GHL |

For VSL/sales pages: full migration to optimized standalone. For multi-page sites: subdomain migration with redirect from main domain.

## Forms (lead capture)

GHL forms POST to GHL's backend. When migrating:

1. Get form embed code from GHL: Form → Integrate → Inline embed
2. Replace standalone form with GHL embed:
```html
<iframe src="https://api.leadconnectorhq.com/widget/form/FORM_ID" id="lead-form" style="width:100%;border:0;height:600px"></iframe>
<script src="https://link.msgsndr.com/js/form_embed.js"></script>
```

3. Or use webhook: GHL → Workflow with "Custom Webhook" trigger → POST from your form:
```js
fetch('https://services.leadconnectorhq.com/hooks/...', {
  method:'POST',
  headers:{'Content-Type':'application/json'},
  body: JSON.stringify({email:..., name:...})
});
```

## Migration strategy

1. Don't touch root domain — subdomain `lp.dominio.com`
2. GHL keeps existing funnels at root
3. New optimized pages on subdomain
4. A/B test 50/50 for 1 week (different ad URLs)
5. If new wins → update all ads to subdomain URL
6. Keep GHL for CRM/automations even after migration

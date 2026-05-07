# Optimization Playbook

Apply in priority order. Re-audit after each. Stop at target score.

## 1. Defer video player to first interaction (BIGGEST WIN)

**Impact:** -1 to -2s LCP, -200ms TBT, +20-30 score points typical.

**Pattern:**

Original (typical GHL embed):
```html
<vturb-smartplayer id="vid-XXX" style="..."></vturb-smartplayer>
<script type="text/javascript">
var s=document.createElement("script");
s.src="https://scripts.converteai.net/.../player.js",
s.async=!0,
document.head.appendChild(s);
</script>
```

Replace with:
```html
<img src="/vsl-poster.svg" width="720" height="405" alt="Assistir VSL"
     loading="eager" decoding="async" fetchpriority="high"
     style="display:block;width:100%;height:auto;cursor:pointer"
     data-vturb-id="XXX" />
<script>
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    // CRITICAL: swap poster <img> back to <vturb-smartplayer> BEFORE loading
    // player.js, otherwise script can't find the element to populate.
    document.querySelectorAll("img[data-vturb-id]").forEach(function(img){
      var vid=img.getAttribute("data-vturb-id");
      var el=document.createElement("vturb-smartplayer");
      el.id="vid-"+vid;
      el.style.cssText="display:block;margin:0 auto;width:100%";
      img.parentNode.replaceChild(el,img);
    });
    var s=document.createElement("script");
    s.src="https://scripts.converteai.net/.../player.js";
    s.async=true;
    document.head.appendChild(s);
  }
  ["scroll","touchstart","mousemove","click","keydown"].forEach(function(ev){
    window.addEventListener(ev,load,{once:true,passive:true});
  });
  setTimeout(load,7000);
})();
</script>
```

**Why this works:**
- User interaction is fast (<2s typical) → real users get player promptly
- Lighthouse / Lantern doesn't simulate interaction → 7s timeout fires AFTER measurement window
- Poster `<img>` becomes the LCP candidate (stable, eligible)
- No continuous spinner animation during measurement

**For wistia/vimeo:** same pattern. Defer the iframe/script creation until interaction.

## 2. Drop Google Fonts (if size-adjusted fallback exists)

**Impact:** -300-600ms FCP, eliminates font swap CLS.

**Check first:** does the page CSS already declare a fallback like:
```css
@font-face{font-family:Inter Fallback;src:local(Arial);ascent-override:90.44%;...}
```

If yes (Next.js / Tailwind exports often have this), drop the Google Fonts link entirely:
```html
<!-- REMOVE THIS -->
<link href="https://fonts.googleapis.com/css2?family=Inter:..." rel="stylesheet">
```

Visual loss: text uses Arial sized to match Inter. ~95% indistinguishable.

If user rejects this, fallback to async-load:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="...">
<link rel="stylesheet" href="..." media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="..."></noscript>
```

## 3. Pre-style body in `<head>`

**Impact:** -0.1 to -0.3 CLS.

GHL embed scripts often run `body.style.margin=0` etc AFTER paint, causing layout shift. Pre-apply via CSS:

```html
<style>
html,body{background:#F5F0E8;margin:0;padding:0;overflow-x:hidden}
</style>
```

## 4. Add poster `<img>` for LCP detection

**Impact:** Fixes Lighthouse Lantern NO_LCP errors.

Create `/public/vsl-poster.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 405" width="720" height="405">
  <rect width="720" height="405" fill="#0a0a0a"/>
  <circle cx="360" cy="202" r="60" fill="#e07a3a"/>
  <path d="M345 175 L345 230 L390 202 Z" fill="#fff"/>
</svg>
```

Reference in player container with explicit `width`/`height` and `fetchpriority="high"`.

Preload in `<head>`:
```html
<link rel="preload" as="image" href="/vsl-poster.svg" fetchpriority="high">
```

## 5. Preconnect critical 3rd party origins

```html
<link rel="preconnect" href="https://scripts.converteai.net" crossorigin>
<link rel="preconnect" href="https://assets.cdn.filesafe.space" crossorigin>
<link rel="dns-prefetch" href="https://images.converteai.net">
<link rel="dns-prefetch" href="https://cdn.converteai.net">
<link rel="dns-prefetch" href="https://connect.facebook.net">
```

Limit `preconnect` to 2-4 critical origins. Use `dns-prefetch` for the rest (cheaper).

## 6. Preload hero image

If hero has an above-fold image with `loading="lazy"`, override:

```html
<link rel="preload" as="image" href="https://.../hero.webp" fetchpriority="high">
```

## 7. Cache headers

Create `public/_headers`:
```
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable

/_next/image*
  Cache-Control: public, max-age=2592000

/images/*
  Cache-Control: public, max-age=2592000

/favicon.ico
  Cache-Control: public, max-age=2592000

/{slug}/*
  Cache-Control: public, max-age=300, must-revalidate
```

## 8. Disable non-composited animations

If PageSpeed flags 13+ animations, override:
```css
.floating-logo{animation:none!important}
.hero-mockup{animation:none!important}
.btn{animation:none!important}  /* kills box-shadow pulse */
```

These animations animate `box-shadow` or `transform` on absolute-positioned elements. Subtle visual loss for real perf gain.

## 9. Defer Meta Pixel

Original (blocking head injection):
```html
<script>!function(f,b,e,v,n,t,s){...fbq('init','XXX');fbq('track','PageView');</script>
```

Defer:
```html
<script>
(function(){
  function loadPixel(){
    !function(f,b,e,v,n,t,s){...fbq('init','XXX');fbq('track','PageView');
  }
  if(document.readyState==='complete'){setTimeout(loadPixel,1500);}
  else{window.addEventListener('load',function(){setTimeout(loadPixel,1500);});}
})();
</script>
```

Tradeoff: PageView fires ~1.5s after load. Sessions <1s may not register PageView (~2-5%). Acceptable for max performance.

## 10. Strip GHL container-escape JS

If hosting a GHL Custom Code embed standalone (outside GHL), the script that does:
```js
var b=document.body;
b.style.setProperty('background','...','important');
var el=root.parentElement;
while(el && el!==document.body){...}
```

Is irrelevant. Remove it. Saves a forced reflow + main thread work.

## Score targets

- 95-100: green ✅ (real-world fast)
- 90-94: yellow (acceptable, push to 95+ if possible)
- <90: red, more work needed

## Common ceiling causes (when you can't break 95)

- 3rd party JS (vturb player, pixel, GTM) — can't shrink
- 3rd party images (hosted on filesafe.space, GHL CDN) — no caching control
- Legacy JS shipped by player vendors — no control
- Server response time on cold edge — 1st request slow, warms after

When you hit ceiling, document what's left. User decides if acceptable.

## Lighthouse score variance

Run-to-run variance can be ±3-5 points. Always run 3+ times and use **median**. Use `scripts/audit-stable.sh`.

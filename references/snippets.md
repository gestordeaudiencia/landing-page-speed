# Code Snippets

Copy-paste building blocks. Adapt placeholders.

## Vturb player deferred

```html
<!-- Replace <vturb-smartplayer> with this poster: -->
<img src="/vsl-poster.svg" width="720" height="405" alt="Assistir VSL"
     loading="eager" decoding="async" fetchpriority="high"
     style="display:block;width:100%;height:auto;cursor:pointer"
     data-vturb-id="69e17684237c448f77dcacae" />

<!-- Replace inline vturb script with: -->
<script>
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    var s=document.createElement("script");
    s.src="https://scripts.converteai.net/ACCOUNT_ID/players/PLAYER_ID/v4/player.js";
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

## Wistia player deferred

```html
<div class="wistia_responsive_wrapper" style="...">
  <img src="/vsl-poster.svg" ... data-wistia-id="VIDEO_ID" />
</div>
<script>
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    var s=document.createElement("script");
    s.src="https://fast.wistia.com/embed/medias/VIDEO_ID.jsonp";
    s.async=true;
    document.head.appendChild(s);
    var s2=document.createElement("script");
    s2.src="https://fast.wistia.com/assets/external/E-v1.js";
    s2.async=true;
    document.head.appendChild(s2);
  }
  ["scroll","touchstart","mousemove","click","keydown"].forEach(function(ev){
    window.addEventListener(ev,load,{once:true,passive:true});
  });
  setTimeout(load,7000);
})();
</script>
```

## Vimeo / YouTube iframe lazy

```html
<a href="https://www.youtube.com/watch?v=VIDEO_ID" id="yt-link"
   style="position:relative;display:block;aspect-ratio:16/9;background:#000">
  <img src="https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg"
       width="640" height="360" alt="Play"
       style="width:100%;height:100%;object-fit:cover" loading="eager" fetchpriority="high"/>
</a>
<script>
document.getElementById('yt-link').addEventListener('click',function(e){
  e.preventDefault();
  var iframe=document.createElement('iframe');
  iframe.src='https://www.youtube.com/embed/VIDEO_ID?autoplay=1';
  iframe.allow='autoplay; fullscreen';
  iframe.style='position:absolute;inset:0;width:100%;height:100%;border:0';
  this.appendChild(iframe);
});
</script>
```

## Meta Pixel deferred 1.5s after load

```html
<script>
(function(){
  function loadPixel(){
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init','PIXEL_ID');
    fbq('track','PageView');
  }
  if(document.readyState==='complete'){setTimeout(loadPixel,1500);}
  else{window.addEventListener('load',function(){setTimeout(loadPixel,1500);});}
})();
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=PIXEL_ID&amp;ev=PageView&amp;noscript=1"/></noscript>
```

## GTM deferred

```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-XXXXX');
  },2000);
});
</script>
```

## Pre-style body (kills script-driven CLS)

```html
<style>
html,body{background:#FFFFFF;margin:0;padding:0;overflow-x:hidden}
.animate-up{opacity:1!important;transform:translateY(0)!important;transition:none!important}
.floating-logo{animation:none!important}
.hero-mockup{animation:none!important}
.btn{animation:none!important}
</style>
```

## Standard `<head>` perf block

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESCRIPTION}">

<link rel="preconnect" href="https://PLAYER_CDN" crossorigin>
<link rel="preconnect" href="https://IMAGE_CDN" crossorigin>
<link rel="dns-prefetch" href="https://connect.facebook.net">
<link rel="dns-prefetch" href="https://www.googletagmanager.com">

<link rel="preload" as="image" href="/vsl-poster.svg" fetchpriority="high">
<link rel="preload" as="image" href="https://IMAGE_CDN/hero.webp">

<link rel="icon" href="/favicon.ico">
```

## Cloudflare Pages `_headers` cache config

```
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable

/_next/image*
  Cache-Control: public, max-age=2592000

/images/*
  Cache-Control: public, max-age=2592000
/videos/*
  Cache-Control: public, max-age=2592000

/favicon.ico
  Cache-Control: public, max-age=2592000

/{slug-1}/*
  Cache-Control: public, max-age=300, must-revalidate
```

## Astro index.astro hub (lists deployed LPs)

```astro
---
const lps = [
  { slug: 'comece2', titulo: 'Variante A' },
  { slug: 'comeceagora', titulo: 'Variante B' },
];
---
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>LP Hub</title>
    <style>
      body { font-family: system-ui; max-width: 720px; margin: 4rem auto; padding: 0 1.5rem; }
      a { display: block; padding: 1rem; border: 1px solid #e5e5e5; border-radius: 8px; margin-bottom: 0.75rem; text-decoration: none; color: #1a1a1a; }
      a:hover { background: #fafafa; }
    </style>
  </head>
  <body>
    <h1>LP Hub</h1>
    {lps.map(lp => (
      <a href={`/${lp.slug}`}>/{lp.slug} — {lp.titulo}</a>
    ))}
  </body>
</html>
```

## Astro config

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  build: { inlineStylesheets: 'auto' },
});
```

## VSL poster SVG (vsl-poster.svg)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 405" width="720" height="405" preserveAspectRatio="xMidYMid slice">
  <defs>
    <radialGradient id="g" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#2a2a2a"/>
      <stop offset="100%" stop-color="#0a0a0a"/>
    </radialGradient>
  </defs>
  <rect width="720" height="405" fill="url(#g)"/>
  <circle cx="360" cy="202" r="60" fill="#e07a3a"/>
  <path d="M345 175 L345 230 L390 202 Z" fill="#fff"/>
  <text x="360" y="320" text-anchor="middle" fill="#999" font-family="Arial,sans-serif" font-size="22" font-weight="600">Clique para assistir</text>
</svg>
```

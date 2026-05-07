# Pixel & Analytics Defer Patterns

Universal rule: defer all tracking pixels 1.5s after `load` event. Tradeoff: ~2-5% sessions <1s lose PageView. Acceptable for performance.

## Universal defer wrapper

```html
<script>
(function(){
  function loadTracking(){
    // ... your pixel init code
  }
  if(document.readyState==='complete'){
    setTimeout(loadTracking,1500);
  } else {
    window.addEventListener('load',function(){setTimeout(loadTracking,1500)});
  }
})();
```

---

## Meta Pixel (Facebook)

**Detection:** `fbq('init', 'PIXEL_ID')` in any script

**Optimized:**
```html
<script>
(function(){
  function loadPixel(){
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init','PIXEL_ID');
    fbq('track','PageView');
  }
  if(document.readyState==='complete'){setTimeout(loadPixel,1500)}
  else{window.addEventListener('load',function(){setTimeout(loadPixel,1500)})}
})();
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=PIXEL_ID&amp;ev=PageView&amp;noscript=1"/></noscript>
```

---

## Google Tag Manager (GTM)

**Detection:** `<script>(function(w,d,s,l,i){...})(window,document,'script','dataLayer','GTM-XXXXX')</script>`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f)})(window,document,'script','dataLayer','GTM-XXXXX');
  },2000);
});
</script>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
```

---

## Google Analytics 4 (GA4 / gtag)

**Detection:** `<script src="https://www.googletagmanager.com/gtag/js?id=G-XXXXX"></script>` + `gtag('config', 'G-XXXXX')`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    var s=document.createElement('script');
    s.src='https://www.googletagmanager.com/gtag/js?id=G-XXXXX';
    s.async=true;
    document.head.appendChild(s);
    window.dataLayer=window.dataLayer||[];
    function gtag(){dataLayer.push(arguments);}
    window.gtag=gtag;
    gtag('js',new Date());
    gtag('config','G-XXXXX');
  },1500);
});
</script>
```

---

## TikTok Pixel

**Detection:** `ttq.load('PIXEL_ID')` or script src `analytics.tiktok.com`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    !function(w,d,t){w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie","holdConsent","revokeConsent","grantConsent"];ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e};ttq.load=function(e,n){var r="https://analytics.tiktok.com/i18n/pixel/events.js",o=n&&n.partner;ttq._i=ttq._i||{};ttq._i[e]=[];ttq._i[e]._u=r;ttq._t=ttq._t||{};ttq._t[e]=+new Date;ttq._o=ttq._o||{};ttq._o[e]=n||{};n=document.createElement("script");n.type="text/javascript";n.async=!0;n.src=r+"?sdkid="+e+"&lib="+t;e=document.getElementsByTagName("script")[0];e.parentNode.insertBefore(n,e)};
      ttq.load('PIXEL_ID');
      ttq.page();
    }(window,document,'ttq');
  },1500);
});
</script>
```

---

## Pinterest Tag

**Detection:** `pintrk('load', 'TAG_ID')` or `s.pinimg.com/ct/core.js`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    !function(e){if(!window.pintrk){window.pintrk=function(){window.pintrk.queue.push(Array.prototype.slice.call(arguments))};var n=window.pintrk;n.queue=[],n.version="3.0";var t=document.createElement("script");t.async=!0,t.src=e;var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(t,r)}}("https://s.pinimg.com/ct/core.js");
    pintrk('load','TAG_ID');
    pintrk('page');
  },1500);
});
</script>
```

---

## LinkedIn Insight Tag

**Detection:** `_linkedin_partner_id = "XXX"` + `snap.licdn.com/li.lms-analytics/insight.min.js`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    var _linkedin_partner_id="PARTNER_ID";
    window._linkedin_data_partner_ids=window._linkedin_data_partner_ids||[];
    window._linkedin_data_partner_ids.push(_linkedin_partner_id);
    var s=document.createElement("script");s.type="text/javascript";s.async=!0;
    s.src="https://snap.licdn.com/li.lms-analytics/insight.min.js";
    document.getElementsByTagName("script")[0].parentNode.insertBefore(s,document.getElementsByTagName("script")[0]);
  },1500);
});
</script>
```

---

## Hotjar

**Detection:** `hj.q` or `static.hotjar.com/c/hotjar-XXX.js`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    (function(h,o,t,j,a,r){h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};h._hjSettings={hjid:HJID,hjsv:6};a=o.getElementsByTagName('head')[0];r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;a.appendChild(r)})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
  },2000);
});
</script>
```

---

## Microsoft Clarity

**Detection:** `clarity.ms/tag/XXX`

**Optimized:**
```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    (function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)})(window,document,"clarity","script","CLARITY_ID");
  },2000);
});
</script>
```

---

## Multiple pixels on same page

Combine into single `setTimeout` callback to avoid multiple `setTimeout` allocations:

```html
<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    // Meta Pixel
    !function(f,b,e,v,n,t,s){...}(...);fbq('init','META_ID');fbq('track','PageView');
    // GTM
    (function(w,d,s,l,i){...})(...,'GTM-XXX');
    // Other pixels...
  },1500);
});
</script>
```

## NoScript fallbacks

Always include `<noscript>` versions for users with JS disabled. Tracking pixels work via 1x1 image:

```html
<noscript>
<img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=PIXEL_ID&amp;ev=PageView&amp;noscript=1"/>
</noscript>
```

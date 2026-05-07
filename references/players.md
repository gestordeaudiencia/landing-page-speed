# Video Player Defer Patterns

For each player type: detection signature + defer-on-interaction pattern.

## Universal pattern

All players follow same structure:
1. Replace player element with poster `<img>` (data URI for zero requests)
2. On first interaction OR 15s timeout: swap img back to original element + load player JS

Poster data URI (reusable):
```
data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 720 405'%3E%3Crect width='720' height='405' fill='%231a1a1a'/%3E%3Ccircle cx='360' cy='202' r='60' fill='%23e07a3a'/%3E%3Cpath d='M345 175L345 230L390 202Z' fill='%23fff'/%3E%3C/svg%3E
```

---

## vturb / converteai

**Detection:**
- `<vturb-smartplayer id="vid-XXX">` element
- Script src contains `scripts.converteai.net`

**Original:**
```html
<vturb-smartplayer id="vid-PLAYER_ID"></vturb-smartplayer>
<script>
var s=document.createElement("script");
s.src="https://scripts.converteai.net/ACCOUNT_ID/players/PLAYER_ID/v4/player.js";
s.async=!0;
document.head.appendChild(s);
</script>
```

**Optimized:**
```html
<img src="data:image/svg+xml,..." width="720" height="405" alt="Assistir VSL"
     loading="eager" decoding="async" fetchpriority="high"
     style="display:block;width:100%;height:auto;cursor:pointer"
     data-vturb-id="PLAYER_ID" />
<script>
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    document.querySelectorAll("img[data-vturb-id]").forEach(function(img){
      var vid=img.getAttribute("data-vturb-id");
      var el=document.createElement("vturb-smartplayer");
      el.id="vid-"+vid;
      el.style.cssText="display:block;margin:0 auto;width:100%";
      img.parentNode.replaceChild(el,img);
    });
    var s=document.createElement("script");
    s.src="https://scripts.converteai.net/ACCOUNT_ID/players/PLAYER_ID/v4/player.js";
    s.async=true;
    document.head.appendChild(s);
  }
  ["scroll","touchstart","mousemove","click","keydown"].forEach(function(ev){
    window.addEventListener(ev,load,{once:true,passive:true});
  });
  setTimeout(load,15000);
})();
</script>
```

---

## Wistia

**Detection:**
- `<div class="wistia_responsive_padding">` or `wistia_embed wistia_async_VIDEO_ID`
- Script src contains `fast.wistia.com` or `fast.wistia.net`

**Original:**
```html
<div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative">
  <div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%">
    <div class="wistia_embed wistia_async_VIDEO_ID seo=true videoFoam=true" style="height:100%;width:100%">&nbsp;</div>
  </div>
</div>
<script src="https://fast.wistia.com/embed/medias/VIDEO_ID.jsonp" async></script>
<script src="https://fast.wistia.com/assets/external/E-v1.js" async></script>
```

**Optimized:**
```html
<div style="position:relative;padding:56.25% 0 0 0;cursor:pointer" data-wistia-placeholder="VIDEO_ID">
  <img src="data:image/svg+xml,..." style="position:absolute;inset:0;width:100%;height:100%"
       alt="Play" loading="eager" fetchpriority="high"/>
</div>
<script>
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    document.querySelectorAll("[data-wistia-placeholder]").forEach(function(div){
      var vid=div.getAttribute("data-wistia-placeholder");
      div.innerHTML='<div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%"><div class="wistia_embed wistia_async_'+vid+' seo=true videoFoam=true" style="height:100%;width:100%">&nbsp;</div></div>';
    });
    var s1=document.createElement("script"); s1.src="https://fast.wistia.com/assets/external/E-v1.js"; s1.async=true;
    document.head.appendChild(s1);
  }
  ["scroll","touchstart","mousemove","click","keydown"].forEach(function(ev){
    window.addEventListener(ev,load,{once:true,passive:true});
  });
  setTimeout(load,15000);
})();
</script>
```

---

## YouTube

**Detection:**
- `<iframe src="https://www.youtube.com/embed/VIDEO_ID">`
- Or `<div class="youtube-embed">` with data attrs

**Optimized — Click to play (best UX + perf):**
```html
<a href="https://www.youtube.com/watch?v=VIDEO_ID" id="yt-VIDEO_ID"
   style="position:relative;display:block;aspect-ratio:16/9;background:#000;text-decoration:none">
  <img src="https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg" alt="Play"
       width="640" height="360"
       style="width:100%;height:100%;object-fit:cover" loading="eager" fetchpriority="high"/>
  <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:80px;height:80px;background:#e07a3aee;border-radius:50%;display:flex;align-items:center;justify-content:center"><span style="color:#fff;font-size:30px;margin-left:5px">▶</span></span>
</a>
<script>
document.getElementById('yt-VIDEO_ID').addEventListener('click',function(e){
  e.preventDefault();
  var iframe=document.createElement('iframe');
  iframe.src='https://www.youtube.com/embed/VIDEO_ID?autoplay=1';
  iframe.allow='autoplay; fullscreen; encrypted-media';
  iframe.style='position:absolute;inset:0;width:100%;height:100%;border:0';
  this.appendChild(iframe);
});
</script>
```

---

## Vimeo

**Detection:** `<iframe src="https://player.vimeo.com/video/VIDEO_ID">`

**Optimized:**
```html
<a href="https://vimeo.com/VIDEO_ID" id="vimeo-VIDEO_ID"
   style="position:relative;display:block;aspect-ratio:16/9;background:#000;text-decoration:none">
  <img src="https://vumbnail.com/VIDEO_ID.jpg" alt="Play"
       style="width:100%;height:100%;object-fit:cover" loading="eager" fetchpriority="high"/>
</a>
<script>
document.getElementById('vimeo-VIDEO_ID').addEventListener('click',function(e){
  e.preventDefault();
  var iframe=document.createElement('iframe');
  iframe.src='https://player.vimeo.com/video/VIDEO_ID?autoplay=1';
  iframe.allow='autoplay; fullscreen; picture-in-picture';
  iframe.style='position:absolute;inset:0;width:100%;height:100%;border:0';
  this.appendChild(iframe);
});
</script>
```

---

## JWPlayer

**Detection:** `<script src="https://cdn.jwplayer.com/.../jwplayer.js">` or `<div id="player"><script>jwplayer(...)</script></div>`

**Optimized — defer entire JWPlayer init:**
```html
<div id="jwplayer-container" style="aspect-ratio:16/9;background:#1a1a1a;cursor:pointer"
     data-jw-config='{"file":"VIDEO_URL","image":"POSTER_URL"}'>
  <img src="data:image/svg+xml,..." style="width:100%;height:100%;object-fit:cover"/>
</div>
<script>
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;
    loaded=true;
    var s=document.createElement("script");
    s.src="https://cdn.jwplayer.com/libraries/YOUR_LIB.js";
    s.onload=function(){
      var c=document.getElementById('jwplayer-container');
      var cfg=JSON.parse(c.getAttribute('data-jw-config'));
      c.innerHTML='';
      jwplayer(c).setup(cfg);
    };
    document.head.appendChild(s);
  }
  ["scroll","touchstart","mousemove","click","keydown"].forEach(function(ev){
    window.addEventListener(ev,load,{once:true,passive:true});
  });
  setTimeout(load,15000);
})();
</script>
```

---

## Panda Video

**Detection:** `<iframe src="https://player-vz-XXX.tv.pandavideo.com.br/...">`

**Optimized:**
```html
<a href="#" id="panda-VIDEO_ID" data-panda-src="https://player-vz-XXX.tv.pandavideo.com.br/..."
   style="position:relative;display:block;aspect-ratio:16/9;background:#000">
  <img src="data:image/svg+xml,..." alt="Play"
       style="width:100%;height:100%;object-fit:cover" loading="eager" fetchpriority="high"/>
</a>
<script>
document.getElementById('panda-VIDEO_ID').addEventListener('click',function(e){
  e.preventDefault();
  var iframe=document.createElement('iframe');
  iframe.src=this.getAttribute('data-panda-src');
  iframe.allow='accelerometer;gyroscope;autoplay;encrypted-media;picture-in-picture';
  iframe.allowFullscreen=true;
  iframe.style='position:absolute;inset:0;width:100%;height:100%;border:0';
  this.appendChild(iframe);
});
</script>
```

---

## Native HTML5 video

**Detection:** `<video src=...>` or `<video><source>...</video>`

**Already lightweight.** Just add `preload="metadata"` and explicit dimensions:
```html
<video src="VIDEO_URL" poster="/poster.webp" controls preload="metadata"
       width="720" height="405" style="display:block;width:100%;height:auto"></video>
```

If video is a VSL (always-play), wrap in click-to-play to defer full file load:
```html
<a href="#" id="vid-link" data-src="VIDEO_URL" style="position:relative;display:block;aspect-ratio:16/9">
  <img src="/poster.webp" loading="eager" fetchpriority="high" style="width:100%"/>
</a>
<script>
document.getElementById('vid-link').addEventListener('click',function(e){
  e.preventDefault();
  var v=document.createElement('video');
  v.src=this.getAttribute('data-src');
  v.controls=true;
  v.autoplay=true;
  v.style='width:100%;height:100%';
  this.replaceWith(v);
});
</script>
```

---

## Detection priority

When detect-stack.py finds multiple players on a page (rare), prioritize:
1. Player in hero/above-fold section (use defer pattern)
2. Players in modals/popups (no defer needed — already hidden)
3. Players below-fold (defer also helps)

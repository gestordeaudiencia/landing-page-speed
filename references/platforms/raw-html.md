# Raw HTML / hand-coded

User has plain HTML file (or pasted HTML). Easiest case.

## Workflow

1. User provides `.html` file path or pastes content
2. Run `python3 scripts/detect-stack.py file.html` to find player/pixel/checkout
3. Apply optimizations via `scripts/build-from-html.py file.html output.html config.json`
4. Deploy

## What to check in raw HTML

### Doctype + structure

If file starts with `<!doctype html>` and has `<html>`, `<head>`, `<body>` — fully formed. Use as-is.

If file starts with `<style>` or `<div>` — it's a fragment/embed. The build script wraps it.

### External CSS/JS

```html
<link rel="stylesheet" href="...">
<script src="..."></script>
```

These are render-blocking. For each:
- **Critical (above-fold styling):** keep but inline if possible
- **Non-critical:** add `async` or `defer` to script tags, use media-trick for CSS

### Image references

Look for:
- `<img src="...">` — keep, but ensure above-fold has `loading="eager"` and `fetchpriority="high"`
- Background images via inline `style` — heavy, consider replacing
- External CDN images — add preconnect to that origin

### Inline scripts

Each `<script>` block:
- Tracking pixel? → wrap in defer (see pixels.md)
- Player init? → wrap in defer (see players.md)
- Form handler? → keep, runs on submit
- Animation/UI logic? → keep but verify no forced reflows

### Forms

Find `<form action="...">`. Test the action URL works from new domain. Common destinations:
- ConvertKit / Mailchimp / ActiveCampaign — endpoints work cross-domain
- Custom backend — verify CORS allows new origin
- GHL webhook — works fine

## Before/after example

### Before (raw HTML, slow)

```html
<!doctype html>
<html>
<head>
<title>VSL</title>
<link href="https://fonts.googleapis.com/css?family=Inter:wght@400;700&display=swap" rel="stylesheet">
<script src="https://connect.facebook.net/en_US/fbevents.js"></script>
<script>
fbq('init','PIXEL_ID');
fbq('track','PageView');
</script>
</head>
<body>
<h1>Headline</h1>
<iframe src="https://player.vimeo.com/video/VIDEO_ID" width="640" height="360"></iframe>
<a href="https://checkout.stripe.com/...">Buy</a>
</body>
</html>
```

### After (optimized)

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VSL</title>
<link rel="preconnect" href="https://i.vimeocdn.com" crossorigin>
<link rel="dns-prefetch" href="https://connect.facebook.net">
<style>
html,body{margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif}
</style>
</head>
<body>
<h1>Headline</h1>

<a href="https://vimeo.com/VIDEO_ID" id="vimeo-link"
   style="position:relative;display:block;aspect-ratio:16/9;background:#000">
  <img src="https://vumbnail.com/VIDEO_ID.jpg" loading="eager" fetchpriority="high"
       style="width:100%;height:100%;object-fit:cover" alt="Play"/>
</a>
<script>
document.getElementById('vimeo-link').addEventListener('click',function(e){
  e.preventDefault();
  var i=document.createElement('iframe');
  i.src='https://player.vimeo.com/video/VIDEO_ID?autoplay=1';
  i.allow='autoplay;fullscreen';
  i.style='position:absolute;inset:0;width:100%;height:100%;border:0';
  this.appendChild(i);
});
</script>

<a href="https://checkout.stripe.com/..." class="btn">Buy</a>

<script>
window.addEventListener('load',function(){
  setTimeout(function(){
    !function(f,b,e,v,n,t,s){...}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init','PIXEL_ID');fbq('track','PageView');
  },1500);
});
</script>
</body>
</html>
```

Result: from ~80 to ~98 Lighthouse mobile.

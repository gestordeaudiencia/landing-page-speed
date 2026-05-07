#!/usr/bin/env python3
"""Wrap a GHL Custom Code embed (or any HTML fragment) into a full standalone HTML
with performance optimizations applied.

Usage:
  python3 build-from-html.py <input.html> <output.html> [config.json]

Config JSON example:
  {
    "title": "My LP — Brand",
    "description": "Page description for SEO + social",
    "vturb_player_url": "https://scripts.converteai.net/<account>/players/<id>/v4/player.js",
    "vturb_player_id": "<id>",
    "pixel_id": "1234567890",
    "checkout_url_old": "https://chk.eduzz.com/OLD",
    "checkout_url_new": "https://lastlink.com/p/CB7B75824/checkout-payment/",
    "preconnect_origins": [
      "https://scripts.converteai.net",
      "https://assets.cdn.filesafe.space"
    ],
    "dns_prefetch_origins": [
      "https://images.converteai.net",
      "https://connect.facebook.net"
    ],
    "preload_hero_image": "https://hosting/hero.webp",
    "drop_google_fonts": true,
    "kill_animations": true,
    "kill_ghl_container_escape": true
  }

If no config passed, sensible defaults applied.
"""
from pathlib import Path
import re
import json
import sys


def patch_body(body: str, cfg: dict) -> str:
    # 1. Drop render-blocking Google Fonts CSS link if requested
    if cfg.get("drop_google_fonts", True):
        body = re.sub(
            r'<link[^>]+href="https://fonts\.googleapis\.com/css2[^"]+"[^>]*>',
            '',
            body,
        )

    # 2. Defer vturb player to first interaction.
    # On load: swap each poster <img data-vturb-id="X"> back to a real
    # <vturb-smartplayer id="vid-X">, THEN inject player.js so it finds them.
    if cfg.get("vturb_player_url"):
        url = cfg["vturb_player_url"]
        deferred = (
            '<script>'
            '(function(){'
            'var loaded=false;'
            'function load(){'
            'if(loaded)return;'
            'loaded=true;'
            'var posters=document.querySelectorAll("img[data-vturb-id]");'
            'posters.forEach(function(img){'
            'var vid=img.getAttribute("data-vturb-id");'
            'var el=document.createElement("vturb-smartplayer");'
            'el.id="vid-"+vid;'
            'el.style.cssText="display:block;margin:0 auto;width:100%";'
            'img.parentNode.replaceChild(el,img);'
            '});'
            'var s=document.createElement("script");'
            's.src="' + url + '";'
            's.async=true;'
            'document.head.appendChild(s);'
            '}'
            'var evs=["scroll","touchstart","mousemove","click","keydown"];'
            'evs.forEach(function(ev){'
            'window.addEventListener(ev,load,{once:true,passive:true});'
            '});'
            'setTimeout(load,15000);'
            '})();'
            '</script>'
        )
        body = re.sub(
            r'<script type="text/javascript">var s2?=document\.createElement\("script"\);s2?\.src="(https://scripts\.converteai\.net/[^"]+)",s2?\.async=!0,document\.head\.appendChild\(s2?\);</script>',
            deferred,
            body,
        )

    # 3. Replace <vturb-smartplayer id="vid-X"> with poster <img data-vturb-id="X">.
    # The deferred loader (above) swaps them back before loading player.js.
    if cfg.get("vturb_player_id"):
        body = re.sub(
            r'<vturb-smartplayer\s+id="vid-([^"]+)"[^>]*></vturb-smartplayer>',
            r'<img src="/vsl-poster.svg" width="720" height="405" alt="Assistir VSL" loading="eager" decoding="async" fetchpriority="high" style="display:block;width:100%;height:auto;cursor:pointer" data-vturb-id="\1" />',
            body,
        )

    # 4. Strip GHL container-escape JS (irrelevant in standalone)
    if cfg.get("kill_ghl_container_escape", True):
        body = re.sub(
            r'// GHL Container Escape.*?el=el\.parentElement;\s*\}',
            '// GHL Container Escape removed (standalone)',
            body,
            flags=re.DOTALL,
        )

    # 5. Strip animate-up IntersectionObserver (CSS override keeps elements visible)
    body = re.sub(
        r"// Animate on scroll.*?root\.querySelectorAll\('\.animate-up'\)\.forEach\(function\(el\)\{obs\.observe\(el\)\}\);",
        '// Animate on scroll disabled (CSS override)',
        body,
        flags=re.DOTALL,
    )

    # 6. Swap checkout URL if specified
    if cfg.get("checkout_url_old") and cfg.get("checkout_url_new"):
        body = body.replace(cfg["checkout_url_old"], cfg["checkout_url_new"])

    return body


def build_head(cfg: dict) -> str:
    title = cfg.get("title", "Landing Page")
    description = cfg.get("description", "")
    preconnects = cfg.get("preconnect_origins", [])
    dns_prefetches = cfg.get("dns_prefetch_origins", [])
    preload_hero = cfg.get("preload_hero_image", "")
    bg_color = cfg.get("body_bg_color", "#ffffff")

    head_lines = [
        '<!doctype html>',
        '<html lang="pt-BR">',
        '<head>',
        '<meta charset="UTF-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        '<meta name="robots" content="index, follow" />',
        f'<title>{title}</title>',
        f'<meta name="description" content="{description}" />',
        '<meta property="og:type" content="website" />',
        f'<meta property="og:title" content="{title}" />',
        f'<meta property="og:description" content="{description}" />',
        '<meta property="og:locale" content="pt_BR" />',
        '<link rel="icon" href="/favicon.ico" />',
        '',
    ]

    for origin in preconnects:
        head_lines.append(f'<link rel="preconnect" href="{origin}" crossorigin />')
    for origin in dns_prefetches:
        head_lines.append(f'<link rel="dns-prefetch" href="{origin}" />')

    head_lines.append('')
    head_lines.append('<link rel="preload" as="image" href="/vsl-poster.svg" fetchpriority="high" />')
    if preload_hero:
        head_lines.append(f'<link rel="preload" as="image" href="{preload_hero}" />')

    head_lines.append('')
    head_lines.append('<style>')
    head_lines.append(f'html,body{{background:{bg_color};margin:0;padding:0;overflow-x:hidden}}')
    head_lines.append('.animate-up{opacity:1!important;transform:translateY(0)!important;transition:none!important}')

    if cfg.get("kill_animations", True):
        head_lines.append('.floating-logo{animation:none!important}')
        head_lines.append('.hero-mockup{animation:none!important}')
        head_lines.append('.btn{animation:none!important}')

    head_lines.append('</style>')
    head_lines.append('</head>')
    head_lines.append('<body>')
    return '\n'.join(head_lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: build-from-html.py <input.html> <output.html> [config.json]")
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    cfg = {}
    if len(sys.argv) >= 4:
        cfg = json.loads(Path(sys.argv[3]).read_text())

    body = src.read_text(encoding="utf-8")
    body = patch_body(body, cfg)

    full_html = build_head(cfg) + '\n' + body + '\n</body>\n</html>\n'

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(full_html, encoding="utf-8")
    print(f"  built {dst}: {len(full_html)} bytes")


if __name__ == "__main__":
    main()

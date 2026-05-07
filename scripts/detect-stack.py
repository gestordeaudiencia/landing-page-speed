#!/usr/bin/env python3
"""Auto-detect technology stack of an HTML landing page.

Usage:
  python3 detect-stack.py <html-file>

Detects (best-effort, returns JSON):
  - Platform / page builder
  - Video player(s) — all instances, with IDs
  - Tracking pixels — Meta, GTM, GA4, TikTok, Pinterest, LinkedIn, Hotjar, Clarity, more
  - Form providers — ConvertKit, Mailchimp, ActiveCampaign, GHL, native HTML
  - Checkout link(s)
  - Fonts source
  - Performance plugins / cache layer
  - Animations / interaction library

Some patterns may be missed if values are loaded dynamically via JS config.
Detector reports best confidence — manual verification recommended for pixel IDs.
"""
import sys
import re
import json
from pathlib import Path


PLATFORMS = [
    ("ghl", [
        r'leadconnectorhq\.com',
        r'data-portal-id',
        r'\.hl_main_popup',
        r'class="hl_page-preview',
        r'stcdn\.leadconnectorhq\.com',
    ]),
    ("elementor-wp", [
        r'wp-content/(plugins|themes|uploads)',
        r'elementor-\d+',
        r'class="elementor[\s-]',
        r'<meta name="generator" content="WordPress',
        r'/wp-includes/',
    ]),
    ("clickfunnels", [
        r'<meta name="generator" content="ClickFunnels',
        r'cf-funnel-step-id',
        r'clickfunnels\.com/track',
        r'cdn\.funnelytics\.io',
    ]),
    ("webflow", [
        r'<meta name="generator" content="Webflow',
        r'data-wf-page',
        r'data-wf-site',
        r'webflow\.[a-f0-9]+\.js',
    ]),
    ("wix", [
        r'<meta name="generator" content="Wix',
        r'static\.wixstatic\.com',
        r'<div id="SITE_ROOT"',
    ]),
    ("kajabi", [
        r'kajabi-cdn\.com',
        r'class="kjbi[-_]',
    ]),
    ("hotmart-pages", [
        r'hotmart\.com/page/',
        r'data-hotmart',
    ]),
    ("kartra", [
        r'pages\.kartra\.com',
        r'class="kt[-_]',
    ]),
    ("cartpanda", [
        r'cartpanda\.com',
    ]),
    ("nextjs-static", [
        r'/_next/static/',
        r'/_next/image\?',
    ]),
    ("astro", [
        r'<meta name="generator" content="Astro',
        r'astro-island',
    ]),
    ("hugo", [
        r'<meta name="generator" content="Hugo',
    ]),
    ("jekyll", [
        r'<meta name="generator" content="Jekyll',
    ]),
]


PLAYERS = [
    ("vturb", [
        r'<vturb-smartplayer\s+id="(?:vid-)?([a-zA-Z0-9_-]+)"',
        r'scripts\.converteai\.net/[a-f0-9-]+/players/([a-f0-9]+)',
    ]),
    ("wistia", [
        r'wistia_async_([a-z0-9]+)',
        r'fast\.wistia\.com/embed/medias/([a-z0-9]+)',
    ]),
    ("vimeo", [
        r'player\.vimeo\.com/video/(\d+)',
        r'vimeo\.com/video/(\d+)',
    ]),
    ("youtube", [
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
    ]),
    ("jwplayer", [
        r'cdn\.jwplayer\.com/libraries/([a-zA-Z0-9]+)',
        r'jwplayer\([\'"]?([\w-]+)[\'"]?\)',
    ]),
    ("panda", [
        r'player-vz-([a-f0-9-]+)\.tv\.pandavideo\.com\.br',
    ]),
    ("html5-video", [
        r'<video[^>]*src="([^"]+)"',
    ]),
]


PIXELS = [
    ("meta-pixel", [
        r"fbq\(['\"]init['\"],\s*['\"](\d+)['\"]",
        r"facebook\.com/tr\?id=(\d+)",
        r"pixelId['\"]\s*:\s*['\"](\d+)['\"]",
        r"['\"]pixel_id['\"]\s*:\s*['\"](\d+)['\"]",
    ]),
    ("gtm", [
        r"GTM-([A-Z0-9]+)",
    ]),
    ("ga4", [
        r"G-([A-Z0-9]{8,})",
        r"gtag\(['\"]config['\"],\s*['\"]G-([A-Z0-9]+)['\"]",
    ]),
    ("ga-universal", [
        r"UA-(\d+-\d+)",
    ]),
    ("tiktok-pixel", [
        r"ttq\.load\(['\"]([A-Z0-9]+)",
    ]),
    ("pinterest", [
        r"pintrk\(['\"]load['\"],\s*['\"](\d+)",
    ]),
    ("linkedin", [
        r"_linkedin_partner_id\s*=\s*['\"](\d+)",
    ]),
    ("hotjar", [
        r"hjid\s*:\s*(\d+)",
    ]),
    ("clarity", [
        r"clarity\.ms/tag/([a-z0-9]+)",
    ]),
    ("twitter-pixel", [
        r"twq\(['\"]init['\"],\s*['\"]([a-z0-9]+)['\"]",
    ]),
]


# Plugin/loader hints — when pixel ID is hidden in dynamic config,
# these markers tell us a pixel IS present even if ID not extracted.
PIXEL_PLUGINS = [
    ("pixelyoursite", r"pixelyoursite|pys[A-Z]"),
    ("pixelcaffeine", r"pixelcaffeine"),
    ("metricool", r"tracker\.metricool\.com"),
    ("fbq-stub", r"fbq\.queue|f\.fbq"),  # any fbq usage
    ("gtag-stub", r"gtag\("),
    ("dataLayer", r"dataLayer\.push"),
]


CHECKOUTS = [
    ("hotmart", r"(?:pay|checkout)\.hotmart\.com[^\"'\s<>]+"),
    ("eduzz", r"(?:chk|sun)\.eduzz\.com/[a-zA-Z0-9]+"),
    ("kiwify", r"pay\.kiwify\.com\.br/[a-zA-Z0-9]+"),
    ("lastlink", r"lastlink\.com/p/[A-Z0-9]+"),
    ("mercadopago", r"mercadopago\.com\.br/checkout|mpago\.la/[a-zA-Z0-9]+"),
    ("stripe", r"checkout\.stripe\.com/[^\"'\s<>]+|buy\.stripe\.com/[^\"'\s<>]+"),
    ("paypal", r"paypal\.com/checkout|paypal\.me/[a-zA-Z0-9]+"),
    ("cartpanda", r"[a-z0-9-]+\.cartpanda\.com/[^\"'\s<>]+"),
    ("perfectpay", r"pay\.perfectpay\.com\.br/[a-zA-Z0-9]+"),
    ("monetizze", r"app\.monetizze\.com\.br/checkout/[^\"'\s<>]+"),
    ("braip", r"(?:ev|app)\.braip\.com/(?:ref|checkout)/[^\"'\s<>]+"),
    ("doppus", r"(?:pay|app)\.doppus\.com/[^\"'\s<>]+"),
    ("clickbank", r"[a-z0-9]+\.pay\.clickbank\.net/[^\"'\s<>]+"),
]


FORMS = [
    ("convertkit", r"forms\.convertkit\.com/(\d+)"),
    ("mailchimp", r"\.us\d+\.list-manage\.com/subscribe"),
    ("activecampaign", r"\.activehosted\.com/proc\.php"),
    ("ghl-form", r"api\.leadconnectorhq\.com/widget/form/([a-zA-Z0-9]+)"),
    ("hubspot-form", r"forms\.hsforms\.com/[a-z0-9]+/[a-z0-9-]+"),
    ("typeform", r"(?:[a-z0-9]+\.)?typeform\.com/to/([a-zA-Z0-9]+)"),
    ("netlify-form", r'<form[^>]+netlify[^>]*>'),
    ("native-html-form", r'<form[^>]+action="(?!#)[^"]+"'),
]


CACHE_PERF = [
    ("wp-rocket", r"wp-rocket"),
    ("litespeed", r"litespeed"),
    ("w3-total-cache", r"w3tc"),
    ("autoptimize", r"autoptimize"),
    ("cloudflare-rocket-loader", r"cloudflare-static/rocket-loader"),
]


ANIMATION_LIBS = [
    ("gsap", r"gsap[/.]|TweenMax|TimelineMax"),
    ("aos", r"aos\.(js|css)|AOS\.init"),
    ("animate-css", r"animate\.css|animate__animated"),
    ("lottie", r"lottiefiles|lottie-player|lottie\.js"),
    ("framer-motion", r"framer-motion"),
]


def find_all_unique(html: str, patterns: list, case_sensitive: bool = False) -> list:
    """Run patterns, return all unique matched groups (or full matches)."""
    found = set()
    flags = 0 if case_sensitive else re.IGNORECASE
    for p in patterns:
        for m in re.finditer(p, html, flags):
            if m.groups():
                found.add(m.group(1))
            else:
                found.add(m.group(0))
    return list(found)


def detect(html: str) -> dict:
    result = {
        "platform": [],
        "players": [],
        "pixels": {},
        "pixel_plugins": [],
        "checkouts": [],
        "forms": [],
        "fonts": [],
        "cache_perf_plugins": [],
        "animation_libs": [],
        "stats": {},
    }

    # Platforms — all that match
    for plat, patterns in PLATFORMS:
        if any(re.search(p, html, re.IGNORECASE) for p in patterns):
            result["platform"].append(plat)

    # Players — collect all unique IDs per player type
    for plr, patterns in PLAYERS:
        ids = find_all_unique(html, patterns)
        if ids:
            result["players"].append({"name": plr, "ids": ids})

    # Pixels — extract IDs case-sensitively (GA4/GTM/UA IDs are uppercase only)
    for px, patterns in PIXELS:
        ids = find_all_unique(html, patterns, case_sensitive=True)
        if ids:
            result["pixels"][px] = ids

    # Pixel plugin hints (when ID is hidden in dynamic config)
    for plug, pattern in PIXEL_PLUGINS:
        if re.search(pattern, html):
            result["pixel_plugins"].append(plug)

    # Checkouts — list URLs
    for ch, pattern in CHECKOUTS:
        urls = list(set(re.findall(pattern, html, re.IGNORECASE)))
        if urls:
            result["checkouts"].append({"name": ch, "urls": urls[:5]})

    # Forms
    for form, pattern in FORMS:
        ids = find_all_unique(html, [pattern])
        if ids:
            result["forms"].append({"provider": form, "matches": ids[:3]})

    # Fonts
    if re.search(r"fonts\.googleapis\.com/css", html):
        result["fonts"].append("google-fonts")
    if re.search(r"use\.typekit\.net", html):
        result["fonts"].append("adobe-fonts")
    if re.search(r"fonts\.bunny\.net", html):
        result["fonts"].append("bunny-fonts")
    if re.search(r"@font-face\s*{[^}]*src:\s*url\([^)]*\.woff2", html):
        result["fonts"].append("self-hosted-woff2")

    # Cache/perf plugins
    for plug, pattern in CACHE_PERF:
        if re.search(pattern, html, re.IGNORECASE):
            result["cache_perf_plugins"].append(plug)

    # Animation libs
    for lib, pattern in ANIMATION_LIBS:
        if re.search(pattern, html, re.IGNORECASE):
            result["animation_libs"].append(lib)

    # Quick stats
    result["stats"] = {
        "html_size_bytes": len(html),
        "script_count": len(re.findall(r"<script[^>]*>", html)),
        "stylesheet_count": len(re.findall(r'rel="stylesheet"', html)),
        "image_count": len(re.findall(r"<img\b", html)),
        "iframe_count": len(re.findall(r"<iframe\b", html)),
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: detect-stack.py <html-file>")
        sys.exit(1)

    src = Path(sys.argv[1])
    html = src.read_text(encoding="utf-8", errors="replace")
    result = detect(html)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

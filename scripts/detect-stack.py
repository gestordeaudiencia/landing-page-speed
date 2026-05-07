#!/usr/bin/env python3
"""Auto-detect technology stack of an HTML landing page.

Usage:
  python3 detect-stack.py <html-file>

Detects:
  - Platform (GHL, Elementor/WP, ClickFunnels, Webflow, Wix, Kajabi, Hotmart, raw)
  - Video player (vturb, wistia, vimeo, youtube, jwplayer, panda, html5)
  - Tracking pixels (Meta, GTM, GA4, TikTok, Pinterest, LinkedIn, Hotjar, Clarity)
  - Checkout link (Hotmart, Eduzz, Kiwify, LastLink, Stripe, PayPal, etc)
  - Fonts (Google Fonts, Adobe Fonts, self-hosted)

Outputs JSON.
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
    ]),
    ("elementor-wp", [
        r'wp-content/(plugins|themes|uploads)',
        r'elementor-\d+',
        r'class="elementor[\s-]',
        r'<meta name="generator" content="WordPress',
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
    ("nextjs-static", [
        r'/_next/static/',
        r'/_next/image\?',
    ]),
]


PLAYERS = [
    ("vturb", [
        r'<vturb-smartplayer',
        r'scripts\.converteai\.net.*players',
    ]),
    ("wistia", [
        r'fast\.wistia\.com',
        r'wistia_async_[a-z0-9]+',
    ]),
    ("vimeo", [
        r'player\.vimeo\.com/video/(\d+)',
    ]),
    ("youtube", [
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
    ]),
    ("jwplayer", [
        r'cdn\.jwplayer\.com',
        r'jwplayer\([\'"]?\w',
    ]),
    ("panda", [
        r'player-vz-[a-f0-9-]+\.tv\.pandavideo\.com\.br',
    ]),
    ("html5-video", [
        r'<video[^>]*src=',
    ]),
]


PIXELS = [
    ("meta-pixel", [
        r"fbq\('init',\s*'(\d+)'",
        r'connect\.facebook\.net/.*fbevents\.js',
    ]),
    ("gtm", [
        r"GTM-[A-Z0-9]+",
        r"googletagmanager\.com/gtm\.js",
    ]),
    ("ga4", [
        r"G-[A-Z0-9]{8,}",
        r"googletagmanager\.com/gtag/js",
    ]),
    ("tiktok-pixel", [
        r"ttq\.load\(['\"]([A-Z0-9]+)",
        r"analytics\.tiktok\.com",
    ]),
    ("pinterest", [
        r"pintrk\(['\"]load['\"]\s*,\s*['\"](\d+)",
        r"s\.pinimg\.com/ct/core\.js",
    ]),
    ("linkedin", [
        r"_linkedin_partner_id\s*=\s*['\"](\d+)",
        r"snap\.licdn\.com/li\.lms-analytics",
    ]),
    ("hotjar", [
        r"hjid:\s*(\d+)",
        r"static\.hotjar\.com/c/hotjar-",
    ]),
    ("clarity", [
        r"clarity\.ms/tag/([a-z0-9]+)",
    ]),
]


CHECKOUTS = [
    ("hotmart", r"(?:pay|checkout)\.hotmart\.com[^\"'\s]+"),
    ("eduzz", r"chk\.eduzz\.com/[a-zA-Z0-9]+"),
    ("kiwify", r"pay\.kiwify\.com\.br/[a-zA-Z0-9]+"),
    ("lastlink", r"lastlink\.com/p/[A-Z0-9]+"),
    ("mercadopago", r"mercadopago\.com\.br/checkout"),
    ("stripe", r"checkout\.stripe\.com/[a-zA-Z0-9_/?-]+"),
    ("paypal", r"paypal\.com/checkout"),
    ("cartpanda", r"cartpanda\.com/[a-zA-Z0-9_/?-]+"),
    ("perfectpay", r"pay\.perfectpay\.com\.br"),
    ("monetizze", r"app\.monetizze\.com\.br/checkout"),
    ("braip", r"(?:ev|app)\.braip\.com/(?:ref|checkout)"),
    ("doppus", r"(?:pay|app)\.doppus\.com"),
]


def detect(html: str) -> dict:
    result = {
        "platform": [],
        "players": [],
        "pixels": {},
        "checkouts": [],
        "fonts": [],
    }

    # Platforms
    for plat, patterns in PLATFORMS:
        for p in patterns:
            if re.search(p, html, re.IGNORECASE):
                result["platform"].append(plat)
                break

    # Players
    for plr, patterns in PLAYERS:
        for p in patterns:
            m = re.search(p, html, re.IGNORECASE)
            if m:
                entry = {"name": plr}
                if m.groups():
                    entry["id"] = m.group(1)
                result["players"].append(entry)
                break

    # Pixels with IDs where possible
    for px, patterns in PIXELS:
        for p in patterns:
            m = re.search(p, html)
            if m:
                if m.groups():
                    result["pixels"][px] = m.group(1)
                else:
                    result["pixels"][px] = True
                break

    # Checkouts
    for ch, pattern in CHECKOUTS:
        matches = re.findall(pattern, html)
        if matches:
            result["checkouts"].append({"name": ch, "urls": list(set(matches[:3]))})

    # Fonts
    if re.search(r"fonts\.googleapis\.com/css", html):
        result["fonts"].append("google-fonts")
    if re.search(r"use\.typekit\.net", html):
        result["fonts"].append("adobe-fonts")
    if re.search(r"@font-face\s*{[^}]*src:\s*url\([^)]*\.woff2", html):
        result["fonts"].append("self-hosted")

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

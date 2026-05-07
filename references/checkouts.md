# Checkout Integration Patterns

Most checkouts are external links — just keep CTA buttons pointing to the checkout URL. No defer needed (link only loads on click).

## Detection patterns

| Service | URL pattern |
|---|---|
| Hotmart | `pay.hotmart.com/`, `*.hotmart.com/checkout` |
| Eduzz | `chk.eduzz.com/`, `sun.eduzz.com/` |
| Kiwify | `pay.kiwify.com.br/`, `kiwify.app/checkout` |
| LastLink | `lastlink.com/p/`, `pay.lastlink.com/` |
| MercadoPago | `mercadopago.com.br/checkout/v1/`, `mpago.la/` |
| Stripe Checkout | `checkout.stripe.com/`, `buy.stripe.com/` |
| PayPal | `paypal.com/checkout`, `paypal.me/` |
| Cartpanda | `seu-checkout.cartpanda.com/` |
| ClickBank | `*.pay.clickbank.net/` |
| Doppus | `pay.doppus.com/`, `app.doppus.com/checkout/` |
| PerfectPay | `pay.perfectpay.com.br/` |
| Monetizze | `app.monetizze.com.br/checkout/` |
| Braip | `ev.braip.com/ref/`, `app.braip.com/checkout/` |

## Performance approach

**Default:** keep checkout links as-is. They don't impact load.

**Anti-pattern (avoid):** loading checkout iframe inline on page load. This is what kills perf. If page does this, ALWAYS replace with click-to-checkout link.

**Pattern (good):**
```html
<a href="https://checkout-url" class="btn">COMPRAR AGORA</a>
```

**Pattern (also good — pixel-tracked redirect):**
```html
<a href="https://checkout-url" class="btn"
   onclick="fbq('track','InitiateCheckout');gtag('event','begin_checkout');return true">
   COMPRAR AGORA
</a>
```

## Inline iframe checkouts (rare, bad for perf)

Some platforms encourage inline checkout iframe (Stripe Checkout embed, custom). If you find:

```html
<iframe src="https://checkout.stripe.com/embed/..."></iframe>
```

Defer with click-to-load:
```html
<button id="open-checkout" class="btn">COMPRAR AGORA</button>
<script>
document.getElementById('open-checkout').addEventListener('click',function(){
  var iframe=document.createElement('iframe');
  iframe.src='https://checkout.stripe.com/embed/...';
  iframe.style='position:fixed;inset:0;width:100vw;height:100vh;z-index:9999;border:0';
  document.body.appendChild(iframe);
});
</script>
```

## Stripe Checkout via JS SDK (best practice)

If using Stripe.js with custom Elements, defer SDK load:
```html
<button id="checkout-btn" class="btn">COMPRAR AGORA</button>
<script>
document.getElementById('checkout-btn').addEventListener('click',async function(){
  if(!window.Stripe){
    await new Promise(function(resolve){
      var s=document.createElement('script');
      s.src='https://js.stripe.com/v3/';
      s.onload=resolve;
      document.head.appendChild(s);
    });
  }
  var stripe=Stripe('pk_live_XXX');
  await stripe.redirectToCheckout({sessionId:'SESSION_ID'});
});
</script>
```

## Conversion tracking on checkout click

Track InitiateCheckout event before redirect (works on both Meta Pixel + GA4):
```html
<a href="https://checkout-url" class="btn" onclick="trackCheckout()">COMPRAR</a>
<script>
function trackCheckout(){
  if(window.fbq) fbq('track','InitiateCheckout');
  if(window.gtag) gtag('event','begin_checkout');
  return true; // continue to href
}
</script>
```

Note: pixel must be loaded by time user clicks. If pixel deferred 1.5s, fast clicks (<1.5s) won't track. Acceptable tradeoff — most users scroll/read before clicking.

## Domain verification (ad platforms)

When migrating page to new subdomain (`lp.dominio.com`):

**Meta Ads:** verification is per-root-domain (`dominio.com`). Subdomain inherits — **no re-verification needed**.

**Google Ads:** same — root domain verification covers subdomains.

**Search Console:** subdomain is separate property. Add it if want SEO data, not required for ads.

**Conversions API (CAPI):** if using server-side events, ensure CAPI endpoint accepts the new hostname. Usually fine without changes — pixel client-side and CAPI server-side are separate flows.

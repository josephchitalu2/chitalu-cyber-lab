# Chitalu Software Solutions: brand guide

This is the brand for everything we ship under the studio name. The positioning
and voice below are a draft built from the logo. Edit any line that does not
sound like you; the rules about colour, contrast and the logo are fixed.

## 1. What the logo says

The mark is a hexagonal **C** with a terminal prompt inside it (`>_`). Read it
literally: a prompt is waiting for an instruction. It is ready, quiet and honest
about what it will do. That is the whole brand:

- **Ready.** Fast pages, clear next step, nothing in the way.
- **Honest.** Plain words. Errors say what happened and how to fix it.
- **Secure by default.** Security is part of the craft, not a feature we mention.
- **Made here.** Software built in Zambia for how people here use it: phones
  first, patchy bandwidth, mobile money, WhatsApp.

Positioning draft (edit freely): *Software that is secure by default and clear
to use.*

## 2. Logo

| File | Use |
| --- | --- |
| `brand/logo.png` | Full lockup on white, paper or light surfaces |
| `brand/logo-reversed.png` | Full lockup on navy or dark surfaces |
| `brand/mark.png` / `mark-reversed.png` | The C alone: avatars, favicons, tight spaces |
| `brand/favicon-32.png`, `apple-touch-icon.png`, `icon-512.png` | Site icons |
| `brand/og-image.png` | Social share card, 1200 x 630 |

**Rules**

- Clear space around the logo: at least the width of the cursor bar (the `_`) on every side.
- Minimum size: lockup 120 px wide, mark 16 px.
- Never recolour it, rotate it, add a shadow, stretch it, or place the navy
  version on a dark background (the wordmark disappears; use the reversed one).
- On a photograph, put the logo on a solid panel, not directly on the image.
- If you can draw the mark as clean vector SVG from your original design file,
  do that and replace the PNGs. PNGs are fine for now.

**Client work keeps the client's brand.** Papino has its own identity. On client
sites, Chitalu appears only as a quiet footer credit (the lockup at about 120 px
wide, linking to the portfolio), never as the site's colours.

## 3. Colour

Taken from the logo: **Electric Blue `#0050FF`** and **Ink Navy `#02162E`**.
Everything else supports them.

| Role | Light | Dark | Notes |
| --- | --- | --- | --- |
| Page background | `#F6F8FC` | `#0A1A33` | |
| Surface (cards, inputs) | `#FFFFFF` | `#12284A` | |
| Text | `#02162E` | `#F6F8FC` | 17:1 / 16:1 |
| Muted text | `#4A5876` | `#A9B8D6` | 6.7:1 / 8.7:1 |
| Brand (buttons, key marks) | `#0050FF` | `#0050FF` | white text on it: 5.85:1 |
| Link | `#0050FF` | `#7FA6FF` | blue is a fill on dark, never text |
| Signal | Ink Navy | `#FFB020` amber | the one warm note; dark surfaces only |
| Success / Warning / Danger | `#0B7A4B` / `#8A5A00` / `#B42318` | `#5BD69B` / `#FFB020` / `#FF8A7A` | always paired with an icon or word |

**Proportion.** Roughly 60% paper or navy, 30% white or deep navy surfaces, 8%
blue, 2% amber. Blue is for the thing you want pressed. If everything is blue,
nothing is.

**Never** rely on colour alone to carry meaning (status needs text or an icon),
and never use a raw hex in a component: use `var(--cs-...)` from
`brand/tokens.css`.

## 4. Type

- **Display: Sora** (700 and 800). Wide and geometric, like the wordmark.
- **Body: IBM Plex Sans** (400, 500, 600). Calm and legible on small screens.
- **Mono: JetBrains Mono.** For prices on a terminal-flavoured page, code, and
  small technical labels. Use sparingly.

Self-host the fonts as subsetted `woff2` with `font-display: swap`. Do not load
them from a third party: it adds a request, leaks visitors' IP addresses, and
breaks a strict Content Security Policy. Keep all fonts under about 60 KB.

Sentence case everywhere. No all-caps labels, no tracked-out eyebrows above every
heading, no one word in a headline picked out in colour. Body lines stay under 70
characters. Use the type scale in the tokens; do not invent sizes.

## 5. Voice

Calm, precise, human. We sound like a good engineer explaining something to a
colleague.

- Plain verbs. Say what the thing does.
- Active voice. The button names the result: **Save changes**, not "Submit".
- One name per action, all the way through. If the button says *Publish*, the
  confirmation says *Published*.
- Errors do not apologise and are never vague. They say what happened and how to
  fix it.
- Empty states invite an action. They do not decorate.
- No hype words: "seamless", "cutting-edge", "revolutionary", "powerful".

| Moment | Not this | This |
| --- | --- | --- |
| Error | "Oops! Something went wrong." | "We couldn't save your changes. Check your connection and try again." |
| Empty | "Nothing here yet." | "No orders yet. New requests appear here the moment they arrive." |
| Success | "Success!" | "Prices saved." |
| Sign-in | "Access denied." | "This area is for the shop's administrator. Sign in with the admin email." |
| Loading | "Please wait..." | "Loading prices" |

## 6. Soul

Spend the boldness in one place. The memorable thing is the **cursor**: the `_`
from the logo, blinking where the next step is.

- **The cursor.** Add `class="cs-cursor"` to one element per page, usually the
  hero line or the primary prompt. It blinks while the page waits for the visitor
  and stays still for anyone who prefers reduced motion. Do not put it on more
  than one element.
- **A signature in the footer.** The lockup plus one line, for example *Built in
  Zambia.* Keep it small and consistent.
- **The 404 page** reads like the terminal it comes from. Example, with a real
  link home:

  ```
  > page not found_
  We couldn't find that page. Go back to the home page or check the address.
  ```
- **Loading** uses the cursor, not a spinner: `Loading prices_`.
- **Small honest touches** that show care: the browser tab title always says what
  page you are on, the form remembers what you typed after an error, and every
  price shows the date it was last updated.

Cut anything decorative that does not help someone do the thing they came for.
Gradient washes, identical rounded cards in a grid, fade-up on every section and
hover effects on everything are the defaults; we choose, we do not default.

## 7. Add the brand to a site

```html
<head>
  <title>Page name | Site name</title>
  <meta name="theme-color" content="#0050FF">
  <link rel="icon" type="image/png" sizes="32x32" href="/brand/favicon-32.png">
  <link rel="apple-touch-icon" href="/brand/apple-touch-icon.png">
  <meta property="og:title" content="Page name">
  <meta property="og:description" content="One plain sentence.">
  <meta property="og:image" content="https://YOUR-DOMAIN/brand/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="/brand/tokens.css">
</head>
```

Use an absolute URL for `og:image`. Replace `og-image.png` with a card that names
the page, once the site has more than one important page.

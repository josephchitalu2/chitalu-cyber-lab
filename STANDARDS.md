# How we ship: UX to UI to production

Every project follows the same seven stages. Each stage has a **gate**: a short
list of things that must be true before moving on. A gate is not a formality. If
one item fails, the work stays in that stage.

```
1 Brief -> 2 UX -> 3 UI -> 4 Build -> 5 Review -> 6 Preview -> 7 Ship -> (operate)
```

## 1. Brief

Write five lines before opening an editor:

1. Who is this for, and on what device? (Assume a phone on a mobile connection.)
2. What is the one thing they came to do?
3. How will we know it worked? (A call, an order, a sign-up, a report read.)
4. What must never happen? (Leaked data, wrong price, locked-out admin.)
5. What is out of scope?

**Gate:** all five answered in the issue or the README.

## 2. UX

- Write the real content first. No lorem ipsum, no placeholder prices.
- One primary action per screen. Name it with a verb.
- Map the flow, including the unhappy paths: empty, error, offline, slow.
- Decide the page's title, headings and link text now. They drive navigation,
  accessibility and search.

**Gate:** a person who has never seen it can find the primary action in five
seconds, and every state (empty, loading, error, success) has written copy.

## 3. UI

- Colours, type, spacing, radii and motion come from `brand/tokens.css`. No raw
  hex values, no one-off font sizes.
- Design phone first at 360 px, then 640, 960 and 1280.
- Every interactive element has all its states: default, hover, focus, active,
  disabled, loading, error.
- Both light and dark themes are checked. Text meets WCAG 2.2 AA: 4.5:1 for body
  text, 3:1 for large text and UI boundaries.
- Tap targets are at least 44 x 44 px.
- Motion: one deliberate moment per page, nothing that loops except the cursor,
  and everything respects `prefers-reduced-motion`.
- Voice follows `BRAND.md`.

**Gate:** screenshots at 360, 768 and 1280 in light and dark, attached to the pull
request, and a contrast check on any colour pair that is not already in the tokens.

## 4. Build

**Quality**
- Semantic HTML first (`button`, `nav`, `main`, headings in order). ARIA only to
  fill a gap that HTML cannot.
- Every image has an `alt` that says what it shows (empty `alt=""` only for decoration).
- Visible keyboard focus. The whole flow works with a keyboard alone.
- Forms: labels tied to inputs, errors in text next to the field, input kept after an error.

**Performance (budgets for a phone on a slow connection)**
- First load under 250 KB gzipped for HTML, CSS and JavaScript together.
- Images as WebP or AVIF, sized for the layout, lazy-loaded below the fold.
- Fonts self-hosted, under 60 KB, with `font-display: swap`.
- Lighthouse on mobile: Performance 90+, Accessibility 100, Best practices 100,
  SEO 95+. A score below target needs a written reason in the pull request.

**Security (every web project)**
- No secrets in the repository, ever. Use platform secrets (`wrangler secret put`,
  GitHub Actions secrets). CI scans for them.
- Security headers on every response: `Content-Security-Policy`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`,
  `Strict-Transport-Security`, and `frame-ancestors 'none'` unless embedding is intended.
- Validate on the server; never trust the interface to enforce a rule.
- Admin areas sit behind real authentication, are not linked publicly, are
  `noindex`, and are checked on every request, not just at login.
- Personal data is minimised, has a retention period, and is deleted on schedule
  (Data Protection Act No. 3 of 2021).
- Dependencies are kept current by Dependabot. Pin and review anything that runs
  in CI.

**Gate:** the project's check command passes locally (see `scripts/ship.sh`).

## 5. Review

Open a pull request even when you are the only reviewer. The template makes you
review your own work as a stranger would: read the diff, run the checklist, look
at the screenshots. Large changes wait a day before merging.

**Gate:** CI is green, the checklist is complete, and the diff has been read top to
bottom once.

## 6. Preview

Look at the real thing before the world does.

- Open it on an actual phone over mobile data, not just a resized desktop window.
- Walk the primary flow from a cold start, as a first-time visitor.
- Try to break it: empty form, long names, a flaky connection, the back button.
- For client work, send the preview link and get a written yes.

**Gate:** the primary flow works on a real phone, and you would be comfortable if
the client opened it right now.

## 7. Ship

You decide when. Shipping is one command from the `main` branch:

```bash
./scripts/ship.sh minor      # or patch / major
```

The script refuses to continue unless:

1. you are on `main`, the working tree is clean, and you are up to date with GitHub;
2. the project's local checks pass;
3. the latest CI run for this exact commit succeeded;

then it shows you what is going out (commits since the last release), and asks you
to type the version number to confirm. Only then does it create a GitHub Release.
Publishing the release triggers `release.yml`, which re-runs the checks and
deploys through the protected **production** environment. The script watches the
deployment and prints the result.

**After every release**
- Run the smoke test: home page loads, primary action works, no console errors,
  security headers present (`curl -sI https://YOUR-SITE | head -20`).
- Keep the previous release's tag handy for rollback:

```bash
./scripts/ship.sh rollback   # redeploys the previous release
```

**Gate:** smoke test passes within ten minutes of release. If it does not, roll
back first and investigate afterwards.

## Operate

- Releases have notes. `gh release create --generate-notes` is the minimum; add one
  human sentence on what changed for the user.
- Backups before any database change (`wrangler d1 export`), kept off the machine.
- Incidents follow the six phases from SEC212: preparation, identification,
  containment, eradication, recovery, lessons learned (blameless).
- Review dependencies, access and secrets every quarter. Remove anything unused.

## Definition of done (copy into the pull request)

- [ ] The brief's one thing works, on a real phone
- [ ] Every state has copy: empty, loading, error, success
- [ ] Tokens only; light and dark checked; contrast verified
- [ ] Keyboard-only walkthrough passes; focus visible; reduced motion respected
- [ ] Within budgets: weight, Lighthouse, fonts
- [ ] No secrets; headers set; admin routes protected; inputs validated server-side
- [ ] CI green; secrets scan green
- [ ] Release notes written; rollback target known

# Chitalu delivery kit

The brand, the standards and the release pipeline for everything shipped under
Chitalu Software Solutions. Drop it into a repository, then ship with one command
when you are satisfied with the build.

```
build -> pull request -> CI (secrets scan + checks) -> you decide -> ./scripts/ship.sh -> production
```

## What is inside

| Path | What it is |
| --- | --- |
| `BRAND.md` | Logo rules, colour, type, voice, and the "soul": the blinking cursor |
| `STANDARDS.md` | The seven stages from brief to production, each with a gate |
| `brand/` | Logo, reversed logo, mark, favicon, touch icon, social card, `tokens.css`, `tokens.json` |
| `scripts/check.sh` | One command for "is this safe?": runs on your laptop and in CI |
| `scripts/ship.sh` | Your release button, built on the GitHub CLI |
| `scripts/deploy.sh` | The only file that knows how this project is deployed |
| `scripts/smoke.sh` | Post-deploy check: site answers, security headers present |
| `scripts/setup-repo.sh` | One-time GitHub settings, security features and branch protection |
| `scripts/bot-publish-data.sh` | Lets scheduled workflows publish without pushing to `main` |
| `.github/workflows/` | `ci.yml`, `release.yml`, `dependabot-auto-merge.yml` |
| `.github/` | `dependabot.yml`, `CODEOWNERS`, PR template, `SECURITY.md`, bug template |
| `docs/AUTO_MAINTENANCE_FIX.md` | Why your pushes keep being rejected, and the fix |

## Install in a repository

```bash
cd ~/chitalu-cyber-lab
KIT=~/Downloads/chitalu-delivery-kit          # wherever you unzipped it

# -n never overwrites a file you already have
cp -rn "$KIT"/.github "$KIT"/scripts "$KIT"/brand "$KIT"/BRAND.md "$KIT"/STANDARDS.md .
cp -rn "$KIT"/docs .
chmod +x scripts/*.sh
git status --short                            # read every file that was added
diff "$KIT"/.github/dependabot.yml .github/dependabot.yml   # merge by hand if different
```

Do not push this straight to `main`. Use the pipeline on itself:

```bash
git switch -c chore/delivery-kit
git add -A && git commit -m "chore: add delivery kit (brand, standards, release pipeline)"
git push -u origin chore/delivery-kit
gh pr create --fill
gh pr checks --watch           # wait for secrets-scan and checks to go green
gh pr merge --squash --delete-branch
git switch main && git pull --rebase origin main
```

Then fix the scheduled workflow (`docs/AUTO_MAINTENANCE_FIX.md`), and run the
one-time setup:

```bash
./scripts/setup-repo.sh                      # safe settings, security features, labels
gh variable set DEPLOY_TARGET --body none    # the lab has nothing to deploy; a release is the deliverable
```

After one scheduled run has passed on the new setup:

```bash
./scripts/setup-repo.sh --protect            # main requires PR + green checks (you can still bypass)
```

## Ship

```bash
./scripts/ship.sh minor --dry-run   # read what it would do
./scripts/ship.sh minor             # patch / minor / major
./scripts/ship.sh rollback          # redeploy the previous release
```

It refuses unless you are on `main`, clean, in sync with GitHub, local checks pass,
and CI is green for the exact commit. It then lists what is going out and makes you
type the version number. The first release in a repo with no tags becomes `v0.1.0`
with `minor`.

## Use it on the other projects

**Papino (Cloudflare Workers).** It is not a Git repository yet. Create one first,
then turn on the pipeline:

```bash
cd ~/papino-chilenje
git init -b main && git add -A && git commit -m "chore: initial import"
gh repo create papino-chilenje --private --source . --push
# copy the kit in as above, then:
./scripts/setup-repo.sh --approve-deploys
gh variable set DEPLOY_TARGET --body cloudflare
gh variable set PRODUCTION_URL --body https://papino-chilenje.chitalu-zm.workers.dev
gh variable set PAPINO_D1_ID --body 42ae73c9-3163-4659-8996-becf3950893b
gh secret set CLOUDFLARE_API_TOKEN --env production     # paste a token scoped to Workers edit
gh secret set CLOUDFLARE_ACCOUNT_ID --env production
```

Create the Cloudflare token in the dashboard (My Profile, API Tokens, "Edit
Cloudflare Workers" template), and store it only as a secret. Papino keeps its own
look: do not use the Chitalu tokens there. Credit the studio in the footer only.

**Portfolio (GitHub Pages).** Pages already publishes from `main`, so a release is
a milestone, not a deploy: set `DEPLOY_TARGET` to `none`, use `BRAND.md` and
`tokens.css` directly, and ship to yourself through pull requests. Add
`STRICT_TOKENS=1` to the check command once the CSS uses the tokens everywhere.

## Not tested

Tested here: every script's syntax, the ship script's gates and dry run against a
stand-in for `gh`, the data-branch publisher against a real Git repository, YAML
validity, and every colour pair for WCAG AA contrast.

Not tested, because it needs your GitHub account: the workflows running on GitHub,
`setup-repo.sh` (it calls GitHub's API), and a real release. Run `setup-repo.sh`
and a `--dry-run` first, and read what each step reports. Check the Actions tab
after the first pull request.

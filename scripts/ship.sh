#!/usr/bin/env bash
# Ship to production with the GitHub CLI.
#
#   ./scripts/ship.sh patch|minor|major [--dry-run]
#   ./scripts/ship.sh rollback [--dry-run]
#
# You decide when. The script refuses to go on unless the tree is clean and on
# main, the local checks pass, and CI is green for this exact commit. Then it shows
# what is going out and waits for you to type the version. Publishing the release
# triggers .github/workflows/release.yml, which deploys through the production
# environment. --dry-run prints every step and changes nothing.
set -euo pipefail

BRANCH="${SHIP_BRANCH:-main}"
CHECK_CMD="${CHECK_CMD:-./scripts/check.sh}"
CI_WORKFLOW="${CI_WORKFLOW:-ci.yml}"
RELEASE_WORKFLOW="${RELEASE_WORKFLOW:-release.yml}"

say()  { printf '> %s\n' "$*"; }
die()  { printf '> stopped: %s\n' "$*" >&2; exit 1; }
usage() { sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-2}"; }

mode=""
dry=0
for arg in "$@"; do
  case "$arg" in
    patch|minor|major|rollback) mode="$arg" ;;
    --dry-run) dry=1 ;;
    -h|--help) usage 0 ;;
    *) usage 2 ;;
  esac
done
[ -n "$mode" ] || usage 2

# run: do it, or in a dry run only say what would happen.
run() {
  if [ "$dry" = 1 ]; then printf '> [dry run] %s\n' "$*"; else "$@"; fi
}

command -v git >/dev/null || die "git is not installed"
command -v gh  >/dev/null || die "the GitHub CLI is not installed (sudo pacman -S github-cli)"
gh auth status >/dev/null 2>&1 || die "not signed in to GitHub. Run: gh auth login"
cd "$(git rev-parse --show-toplevel)"

# Wait for the release workflow that belongs to a tag, then follow it to the end.
watch_release() {
  local tag="$1" id=""
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    id=$(gh run list --workflow "$RELEASE_WORKFLOW" --limit 10 --json databaseId,headBranch \
           --jq "[.[] | select(.headBranch == \"$tag\")] | .[0].databaseId // empty" 2>/dev/null || true)
    [ -n "$id" ] && break
    sleep 5
  done
  [ -n "$id" ] || die "could not find the release workflow run. Check: gh run list --workflow $RELEASE_WORKFLOW"
  say "watching deployment (run $id)"
  gh run watch "$id" --exit-status
}

# ---------------------------------------------------------------- rollback
if [ "$mode" = "rollback" ]; then
  mapfile -t tags < <(gh release list --limit 2 --json tagName --jq '.[].tagName')
  [ "${#tags[@]}" -ge 2 ] || die "need at least two releases to roll back"
  current="${tags[0]}"; previous="${tags[1]}"
  say "live release: $current"
  say "rolling back to: $previous"
  say "this redeploys the old code; it does not undo database changes"
  if [ "$dry" = 0 ]; then
    printf '> type the tag to confirm (%s): ' "$previous"
    read -r answer
    [ "$answer" = "$previous" ] || die "not confirmed, nothing changed"
  fi
  run gh workflow run "$RELEASE_WORKFLOW" -f ref="$previous"
  if [ "$dry" = 0 ]; then
    sleep 6
    id=$(gh run list --workflow "$RELEASE_WORKFLOW" --limit 1 --json databaseId --jq '.[0].databaseId')
    gh run watch "$id" --exit-status
    say "rolled back to $previous. Run the smoke test, then find the cause."
  fi
  exit 0
fi

# -------------------------------------------------------------------- ship
say "preflight"
[ "$(git branch --show-current)" = "$BRANCH" ] || die "switch to $BRANCH first (you are on $(git branch --show-current))"
[ -z "$(git status --porcelain)" ] || die "uncommitted changes. Commit or stash them first"
git fetch --quiet origin "$BRANCH" --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")" ] \
  || die "$BRANCH is not in sync with GitHub. Run: git pull --rebase origin $BRANCH (or git push)"

say "local checks"
[ -x "$CHECK_CMD" ] || die "check script $CHECK_CMD not found or not executable"
"$CHECK_CMD"

say "CI for this commit"
sha=$(git rev-parse HEAD)
line=$(gh run list --workflow "$CI_WORKFLOW" --commit "$sha" --limit 1 \
         --json databaseId,status,conclusion \
         --jq '.[0] | "\(.databaseId) \(.status) \(.conclusion)"' 2>/dev/null || true)
[ -n "$line" ] && [ "$line" != "null null null" ] \
  || die "no CI run found for $sha. Push it and wait for CI"
read -r ci_id ci_status ci_conclusion <<<"$line"
if [ "$ci_status" != "completed" ]; then
  say "CI is $ci_status, waiting"
  gh run watch "$ci_id" --exit-status || die "CI failed. Fix it before shipping"
  ci_conclusion=$(gh run view "$ci_id" --json conclusion --jq .conclusion)
fi
[ "$ci_conclusion" = "success" ] || die "CI concluded '$ci_conclusion'. Fix it before shipping"
say "CI is green"

last=$(git tag --list 'v[0-9]*.[0-9]*.[0-9]*' --sort=-v:refname | head -n 1)
last="${last:-v0.0.0}"
IFS=. read -r maj min pat <<<"${last#v}"
case "$mode" in
  major) maj=$((maj + 1)); min=0; pat=0 ;;
  minor) min=$((min + 1)); pat=0 ;;
  patch) pat=$((pat + 1)) ;;
esac
next="v$maj.$min.$pat"

range="$last..HEAD"
git rev-parse -q --verify "refs/tags/$last" >/dev/null || range="HEAD"
count=$(git rev-list --count "$range")
[ "$count" -gt 0 ] || die "nothing new since $last"

echo
say "going out: $last -> $next ($count commits)"
(git log --oneline --no-decorate "$range" || true) | head -n 20
[ "$count" -le 20 ] || echo "  ... and $((count - 20)) more"
echo
open_prs=$(gh pr list --state open --json number --jq 'length' 2>/dev/null || echo "?")
say "open pull requests: $open_prs"

if [ "$dry" = 0 ]; then
  printf '> type the version to ship it (%s): ' "$next"
  read -r answer
  [ "$answer" = "$next" ] || die "not confirmed, nothing changed"
fi

run gh release create "$next" --target "$BRANCH" --title "$next" --generate-notes
if [ "$dry" = 0 ]; then
  watch_release "$next"
  say "shipped. $next is live."
  gh release view "$next" --json url --jq '.url'
  say "next: smoke test the site. If it is wrong, roll back first: ./scripts/ship.sh rollback"
fi

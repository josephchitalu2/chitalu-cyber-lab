#!/usr/bin/env bash
# Publish generated files (threat intel, risk register, telemetry) to a separate
# `data` branch instead of pushing to main.
#
#   ./scripts/bot-publish-data.sh data/latest_iocs.txt reports/RISK_REGISTER.md ...
#
# Why: when a scheduled workflow pushes to main, your own pushes get rejected
# ("fetch first") and main can never be protected. On the data branch, the bot owns
# the history and main stays yours. Files keep their relative paths.
set -euo pipefail

branch="${DATA_BRANCH:-data}"
[ "$#" -gt 0 ] || { echo "usage: $0 file [file...]" >&2; exit 2; }

cd "$(git rev-parse --show-toplevel)"
tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp/wt" >/dev/null 2>&1 || true; rm -rf "$tmp"' EXIT

# Copy the files out of the tree first, so switching branches cannot clash with them.
for f in "$@"; do
  [ -f "$f" ] || { echo "missing file: $f" >&2; exit 1; }
  mkdir -p "$tmp/out/$(dirname "$f")"
  cp "$f" "$tmp/out/$f"
done

git config user.name  >/dev/null || git config user.name  "github-actions[bot]"
git config user.email >/dev/null || git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  git fetch --quiet origin "$branch"
  git worktree add --quiet -B "$branch" "$tmp/wt" "origin/$branch"
else
  git worktree add --quiet --detach "$tmp/wt"
  git -C "$tmp/wt" switch --quiet --orphan "$branch"
  git -C "$tmp/wt" rm -rfq . >/dev/null 2>&1 || true
fi

cp -R "$tmp/out/." "$tmp/wt/"
git -C "$tmp/wt" add -A
if git -C "$tmp/wt" diff --cached --quiet; then
  echo "Data branch already up to date."
  exit 0
fi
git -C "$tmp/wt" commit --quiet -m "chore(data): refresh generated reports ($(date -u '+%F %H:%M')Z)"
git -C "$tmp/wt" push --quiet origin "HEAD:refs/heads/$branch"
echo "Published to $branch."

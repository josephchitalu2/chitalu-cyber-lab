#!/usr/bin/env bash
# One-time repository setup with the GitHub CLI. Safe to run again.
#
#   ./scripts/setup-repo.sh                  settings, security features, labels, production environment
#   ./scripts/setup-repo.sh --approve-deploys  also require your approval before each production deploy
#   ./scripts/setup-repo.sh --protect        also protect main (read the note below first)
#
# NOTE on --protect: it requires pull requests and passing checks on main. A bot
# that pushes straight to main (like a scheduled workflow) will be blocked. Move
# such workflows to scripts/bot-publish-data.sh first. Repository admins (you)
# can still push directly.
set -uo pipefail   # no -e on purpose: report every step and carry on

protect=0; approve=0
for arg in "$@"; do
  case "$arg" in
    --protect) protect=1 ;;
    --approve-deploys) approve=1 ;;
    -h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

gh auth status >/dev/null 2>&1 || { echo "Run: gh auth login" >&2; exit 1; }
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner) || exit 1

ok()   { printf '  ok    %s\n' "$1"; }
warn() { printf '  skip  %s (%s)\n' "$1" "$2"; }
try()  { local label="$1"; shift; if "$@" >/dev/null 2>&1; then ok "$label"; else warn "$label" "not available on this repo or plan"; fi; }

echo "> $repo"

echo "> merge settings"
try "squash merge only, auto-merge on, delete merged branches" \
  gh repo edit "$repo" --enable-auto-merge --delete-branch-on-merge \
    --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false

echo "> security"
try "Dependabot alerts"               gh api -X PUT "repos/$repo/vulnerability-alerts"
try "Dependabot security updates"     gh api -X PUT "repos/$repo/automated-security-fixes"
try "secret scanning + push protection" gh api -X PATCH "repos/$repo" \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'
try "private vulnerability reporting" gh api -X PUT "repos/$repo/private-vulnerability-reporting"

echo "> labels"
try "needs-review"  gh label create needs-review  --color D93F0B --description "Needs a human before merging" --force
try "dependencies"  gh label create dependencies  --color 0050FF --description "Dependency updates" --force
try "automated"     gh label create automated     --color 02162E --description "Opened by automation" --force

echo "> production environment"
if [ "$approve" = 1 ]; then
  uid=$(gh api user --jq .id)
  printf '{"reviewers":[{"type":"User","id":%s}]}' "$uid" | try "production, approval required" \
    gh api -X PUT "repos/$repo/environments/production" --input -
else
  try "production" gh api -X PUT "repos/$repo/environments/production"
fi

if [ "$protect" = 1 ]; then
  echo "> protecting main"
  existing=$(gh api "repos/$repo/rulesets" --jq '.[] | select(.name == "protect-main") | .id' 2>/dev/null || true)
  if [ -n "$existing" ]; then
    ok "ruleset protect-main already exists (id $existing)"
  else
    read -r -p "  Anything that pushes straight to main will be blocked. Continue? [y/N] " yn
    if [ "$yn" = "y" ] || [ "$yn" = "Y" ]; then
      cat <<'JSON' | try "ruleset protect-main" gh api -X POST "repos/$repo/rulesets" --input -
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [ { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" } ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [ { "context": "checks" }, { "context": "secrets-scan" } ] } }
  ]
}
JSON
    else
      echo "  skipped"
    fi
  fi
fi

echo "> done. Next: set repository variables (Settings > Variables): DEPLOY_TARGET, PRODUCTION_URL."

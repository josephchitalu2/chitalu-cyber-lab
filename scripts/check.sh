#!/usr/bin/env bash
# One command for "is this safe to merge or ship?". It runs on your laptop and in
# CI (ci.yml, release.yml), so green here means green on GitHub.
# Add project-specific checks at the bottom; keep the groups short and fast.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

groups=0
step() { printf '\n== %s\n' "$1"; groups=$((groups + 1)); }

step "Workflow and config YAML parses"
python3 - <<'PY'
import glob, sys
try:
    import yaml
except ImportError:
    print("  (pyyaml not installed, skipping)")
    sys.exit(0)
bad = 0
for f in glob.glob(".github/**/*.yml", recursive=True):
    try:
        yaml.safe_load(open(f, encoding="utf-8"))
    except Exception as e:
        print(f"  {f}: {e}")
        bad = 1
sys.exit(bad)
PY

if compgen -G "scripts/*.sh" >/dev/null; then
  step "Shell scripts"
  for f in scripts/*.sh; do bash -n "$f"; done
  if command -v shellcheck >/dev/null 2>&1; then
    shellcheck scripts/*.sh
  else
    echo "  (shellcheck not installed: syntax-checked only)"
  fi
fi

if [ -n "$(git ls-files '*.py' | head -n 1)" ]; then
  step "Python compiles"
  git ls-files -z '*.py' | xargs -0 -n1 python3 -c \
    'import sys; compile(open(sys.argv[1], encoding="utf-8").read(), sys.argv[1], "exec")'
  if [ -d tests ] || [ -n "$(git ls-files 'test_*.py' '*_test.py' | head -n 1)" ]; then
    if python3 -m pytest --version >/dev/null 2>&1; then
      step "Python tests"
      python3 -m pytest -q
    else
      echo "  (pytest not installed: tests not run)"
    fi
  fi
fi

if [ -f package.json ]; then
  step "Node lint and tests"
  [ -d node_modules ] || npm ci
  npm run lint --if-present
  npm test --if-present
fi

# Opt in for sites that use the Chitalu brand: STRICT_TOKENS=1 ./scripts/check.sh
if [ "${STRICT_TOKENS:-0}" = "1" ]; then
  step "Design tokens only (no raw hex colours outside brand/tokens.css)"
  hits=$(git ls-files -z '*.css' ':!brand/tokens.css' | xargs -0 -r grep -nE '#[0-9A-Fa-f]{3,8}\b' || true)
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits"
    echo "Raw hex colours found above. Use var(--cs-...) from brand/tokens.css." >&2
    exit 1
  fi
fi

# Local secrets scan. In CI the gitleaks action does this instead.
if [ -z "${CI:-}" ] && command -v gitleaks >/dev/null 2>&1; then
  step "Secrets scan (gitleaks)"
  gitleaks detect --source . --redact --no-banner
fi

printf '\nAll %d check groups passed.\n' "$groups"

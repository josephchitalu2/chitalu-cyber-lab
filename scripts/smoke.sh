#!/usr/bin/env bash
# Quick post-deploy check: the site answers, and the security headers are there.
# Usage: scripts/smoke.sh https://your-site.example
# Make missing headers fail the run with SMOKE_STRICT_HEADERS=1.
set -euo pipefail
url="${1:?usage: smoke.sh URL}"

code=000
for attempt in 1 2 3 4 5 6; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" || true)
  [ "$code" = "200" ] && break
  echo "attempt $attempt: HTTP $code, retrying in 10s"
  sleep 10
done
[ "$code" = "200" ] || { echo "FAIL: $url returned HTTP $code" >&2; exit 1; }
echo "OK: $url returned 200"

headers=$(curl -sI --max-time 15 "$url" | tr -d '\r' | tr '[:upper:]' '[:lower:]')
missing=0
for h in content-security-policy x-content-type-options referrer-policy; do
  if ! printf '%s\n' "$headers" | grep -q "^$h:"; then
    echo "WARN: missing security header: $h"
    missing=1
  fi
done
if [ "$missing" = 1 ] && [ "${SMOKE_STRICT_HEADERS:-0}" = "1" ]; then
  exit 1
fi

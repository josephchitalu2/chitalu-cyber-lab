#!/usr/bin/env bash
# Called by .github/workflows/release.yml after the checks pass, with the release
# tag checked out. This is the only file that knows how THIS project is deployed.
# Set the repository variable DEPLOY_TARGET (Settings > Variables) to choose.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

case "${DEPLOY_TARGET:-none}" in
  none)
    echo "Nothing to deploy for this project: the tagged release is the deliverable."
    ;;
  cloudflare)
    # A Cloudflare Workers app built with `npm run build:cloudflare` (the Papino setup).
    # Needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID on the production environment,
    # and PAPINO_D1_ID as a repository variable.
    npm ci
    npm run build:cloudflare
    npx wrangler deploy --config dist/server/wrangler.json
    ;;
  *)
    echo "Unknown DEPLOY_TARGET '${DEPLOY_TARGET}'. Edit scripts/deploy.sh." >&2
    exit 1
    ;;
esac

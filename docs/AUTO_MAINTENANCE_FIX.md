# Fix: the scheduled workflow keeps rejecting your pushes

## What is happening

`auto-maintenance.yml` commits refreshed files straight to `main` every 12 hours.
Your own pushes then fail with `rejected ... (fetch first)`, and you end up
stashing, rebasing and force-resolving by hand. It will also block branch
protection on `main`, because a protected branch refuses direct pushes.

## The fix

Let the bot own a separate `data` branch. `main` stays yours. In
`.github/workflows/auto-maintenance.yml`:

1. Give the workflow write access to contents and stop two runs overlapping:

```yaml
permissions:
  contents: write

concurrency:
  group: auto-maintenance
  cancel-in-progress: false
```

2. Replace the last step ("Commit updated intelligence & GRC reports") with:

```yaml
      - name: Publish refreshed data (never touches main)
        run: ./scripts/bot-publish-data.sh data/latest_iocs.txt data/ecs_telemetry.ndjson reports/RISK_REGISTER.md
```

3. Make sure the job's checkout step does not use `persist-credentials: false`
   (the script pushes with the checkout's token).

The files now live on the `data` branch with the same paths. Update any README
link to the risk register to point at that branch:
`https://github.com/josephchitalu2/chitalu-cyber-lab/blob/data/reports/RISK_REGISTER.md`

Once this is merged and one scheduled run has succeeded, it is safe to run
`./scripts/setup-repo.sh --protect`.

## Also check

- `python3 main.py ship-elk` runs on a GitHub-hosted runner. It cannot reach an
  ELK stack running on your laptop (`localhost`) or inside your home network. If it
  targets one, the step either fails or ships nothing. Point it at a reachable
  endpoint, store the URL and credentials as Actions secrets, and make sure
  nothing prints them in the logs.
- Pin third-party actions to a commit SHA once things are stable (Dependabot keeps
  SHA pins updated). In a security portfolio, an unpinned action is the first
  thing a reviewer will notice.

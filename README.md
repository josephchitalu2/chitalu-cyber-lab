# Chitalu Cyber Lab

An automated attack-surface drift monitor and threat intelligence aggregator built in Python.

## Architecture
- **`core/database.py`**: SQLite state engine tracking port baselines, service banners, and historical drift.
- **`collectors/net_monitor.py`**: Multi-threaded port & banner scanner that alerts on newly exposed ports or banner changes.
- **`collectors/threat_intel.py`**: Live feed collector ingesting **Abuse.ch Feodo Tracker** C2 IPs and **CISA KEV** vulnerabilities.
- **`.github/workflows/sync-threat-intel.yml`**: Automated CI pipeline syncing threat feeds every 12 hours.

## Quick Start
```bash
# Sync live threat intelligence feeds
python3 main.py sync-intel

# Run a stateful baseline scan (run twice to see drift detection in action)
python3 main.py scan 127.0.0.1
```

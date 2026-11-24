# Chitalu Cyber Lab

Automated attack-surface drift monitoring, threat intelligence aggregation, and signature-based security auditing in Python.

## Modules
- **State Engine (`core/database.py`)**: Tracks historical port baselines and service banners in SQLite.
- **Drift Monitor (`collectors/net_monitor.py`)**: Flags newly exposed ports or banner changes across scans.
- **Threat Intel (`collectors/threat_intel.py`)**: Syncs C2 blocklists and known exploited vulnerabilities via scheduled workflows.
- **Log Correlator (`analyzers/log_correlator.py`)**: Hunts for known threat indicators inside local system logs.
- **YAML Scanner (`analyzers/yaml_scanner.py`)**: Tests web targets against declarative YAML signatures in `templates/`.

## CLI Commands
```bash
python3 main.py sync-intel
python3 main.py scan 127.0.0.1
python3 main.py correlate /var/log/auth.log
python3 main.py web-audit http://127.0.0.1:8000
```

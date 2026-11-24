# Chitalu Cyber Lab

A unified, zero-dependency Security Engineering platform covering Attack-Surface Management, Threat Intelligence, GRC Risk Scoring, SOC Telemetry (ELK), Cryptographic Auditing, and Cloud Security Posture Management (CSPM).

## Architecture
- **`core/database.py`**: SQLite state engine tracking historical port baselines, service banners, and IoCs.
- **`collectors/`**: Stateful port drift scanner (`net_monitor.py`) and live Spamhaus DROP / CISA KEV threat feed collector (`threat_intel.py`).
- **`analyzers/`**: Threat-intel log correlator (`log_correlator.py`) and YAML signature web scanner (`yaml_scanner.py`).
- **`crypto_audit/`**: TLS protocol, cipher suite, certificate expiration, and HSTS posture auditor (`tls_auditor.py`).
- **`risk/`**: Quantitative GRC risk scoring engine (`scorer.py`) mapped to NIST CSF and ISO 27001 controls (`reports/RISK_REGISTER.md`).
- **`soc_elk/`**: Elastic Common Schema (ECS) JSON telemetry exporter (`ecs_shipper.py`) and Dockerized ELK Stack pipeline.
- **`cspm/`**: Static Cloud Security Posture Management auditing AWS IAM policies, Terraform (`.tf`), and Dockerfiles against CIS benchmarks.
- **`tests/`**: Automated unit test suite verified on every push via GitHub Actions.

## CLI Usage
```bash
python3 main.py sync-intel
python3 main.py scan 127.0.0.1
python3 main.py correlate /var/log/auth.log
python3 main.py web-audit http://127.0.0.1:8000
python3 main.py tls-audit example.com
python3 main.py risk-report
python3 main.py ship-elk
python3 main.py cloud-audit cspm/lab_targets
```

### Live AWS / LocalStack API Auditing
```bash
# Start emulated AWS APIs locally (S3, IAM, EC2)
docker compose -f cspm/docker-compose.localstack.yml up -d

# Run live API posture audit & update Risk Register / ELK telemetry
python3 main.py aws-live-audit
python3 main.py risk-report
python3 main.py ship-elk
```

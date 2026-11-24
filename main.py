import sys
from collectors.net_monitor import run_monitor
from collectors.threat_intel import init_db, fetch_spamhaus_drop, fetch_cisa_kev, export_ioc_snapshot
from analyzers.log_correlator import correlate_logs
from analyzers.yaml_scanner import run_templates
from risk.scorer import generate_risk_register
from soc_elk.ecs_shipper import ship_to_logstash
from cspm.iac_auditor import run_cspm_audit
from crypto_audit.tls_auditor import audit_tls_endpoint

USAGE = """Chitalu Cyber Lab - Unified Security Engineering & Posture Platform
Usage:
  python3 main.py scan <host>          Run stateful port scan & flag baseline drift
  python3 main.py sync-intel           Pull latest Spamhaus DROP & CISA KEV feeds
  python3 main.py correlate <logfile>  Cross-reference log IPs against live threat intel
  python3 main.py web-audit <url>      Run YAML vulnerability signatures against a target URL
  python3 main.py tls-audit <domain>   Inspect TLS protocol, cipher strength, cert expiry & HSTS
  python3 main.py risk-report          Generate GRC Risk Register mapped to NIST/ISO controls
  python3 main.py ship-elk             Export & ship ECS JSON telemetry to ELK Stack (Logstash)
  python3 main.py cloud-audit [dir]    Audit Terraform (.tf), IAM (.json) & Dockerfiles for CIS flaws
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv
    if cmd == "scan":
        run_monitor(sys.argv if len(sys.argv) > 2 else "127.0.0.1")
    elif cmd == "sync-intel":
        conn = init_db()
        ips = fetch_spamhaus_drop(conn)
        cves = fetch_cisa_kev(conn)
        export_ioc_snapshot(conn)
        print(f"[+] Threat Intel Updated: +{ips} Spamhaus DROP netblocks, +{cves} CVEs")
    elif cmd == "correlate":
        correlate_logs(sys.argv if len(sys.argv) > 2 else "/var/log/auth.log")
    elif cmd == "web-audit":
        run_templates(sys.argv if len(sys.argv) > 2 else "http://127.0.0.1:8000")
    elif cmd == "tls-audit":
        audit_tls_endpoint(sys.argv if len(sys.argv) > 2 else "example.com")
    elif cmd == "risk-report":
        generate_risk_register()
    elif cmd == "ship-elk":
        ship_to_logstash()
    elif cmd == "cloud-audit":
        run_cspm_audit(sys.argv if len(sys.argv) > 2 else "cspm/lab_targets")
    else:
        print(USAGE)

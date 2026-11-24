import sys
from collectors.net_monitor import run_monitor
from collectors.threat_intel import init_db, fetch_feodo_ips, fetch_cisa_kev, export_ioc_snapshot
from analyzers.log_correlator import correlate_logs
from analyzers.yaml_scanner import run_templates
from risk.scorer import generate_risk_register

USAGE = """Chitalu Cyber Lab - Attack Surface, Threat Intel & GRC Engine
Usage:
  python3 main.py scan <host>         Run stateful port scan & flag baseline drift
  python3 main.py sync-intel          Pull latest Abuse.ch Feodo IPs & CISA KEV feeds
  python3 main.py correlate <logfile> Cross-reference log IPs against live threat intel
  python3 main.py web-audit <url>     Run YAML vulnerability signatures against a target URL
  python3 main.py risk-report         Generate GRC Risk Register mapped to NIST/ISO controls
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "scan":
        target = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        run_monitor(target)
    elif cmd == "sync-intel":
        conn = init_db()
        ips = fetch_feodo_ips(conn)
        cves = fetch_cisa_kev(conn)
        export_ioc_snapshot(conn)
        print(f"[+] Threat Intel Updated: +{ips} IPs, +{cves} CVEs")
    elif cmd == "correlate":
        logfile = sys.argv[2] if len(sys.argv) > 2 else "/var/log/auth.log"
        correlate_logs(logfile)
    elif cmd == "web-audit":
        url = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"
        run_templates(url)
    elif cmd == "risk-report":
        generate_risk_register()
    else:
        print(USAGE)

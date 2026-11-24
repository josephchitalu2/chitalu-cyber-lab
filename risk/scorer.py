from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import init_db
from risk.compliance_mapper import map_port_to_controls

HIGH_RISK_PORTS = {21, 23, 3306, 5432, 6379, 9200}

def load_assets(filepath: str = "data/assets.yaml") -> dict:
    assets = {}
    path = Path(filepath)
    if not path.exists():
        return assets

    current_host = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not raw.startswith(" ") and line.endswith(":"):
            current_host = line[:-1].strip()
            assets[current_host] = {"name": current_host, "environment": "unknown", "criticality": 3, "owner": "Unassigned"}
        elif current_host and ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            assets[current_host][k] = int(v) if k == "criticality" else v
    return assets

def calculate_risk_score(port: int, criticality: int, active_kev_count: int) -> tuple:
    base_likelihood = 4 if port in HIGH_RISK_PORTS else 2
    if active_kev_count > 0 and port in {80, 443, 9200}:
        base_likelihood = min(5, base_likelihood + 1)

    raw_score = base_likelihood * criticality  # Scale: 1 to 25
    if raw_score >= 20:
        return (raw_score, "CRITICAL", "24 Hours")
    elif raw_score >= 12:
        return (raw_score, "HIGH", "7 Days")
    elif raw_score >= 6:
        return (raw_score, "MEDIUM", "30 Days")
    return (raw_score, "LOW", "90 Days")

def generate_risk_register() -> None:
    conn = init_db()
    assets = load_assets()
    baselines = conn.execute("SELECT host, port, banner, last_seen FROM port_baselines ORDER BY host, port").fetchall()
    kev_count = conn.execute("SELECT COUNT(*) FROM threat_iocs WHERE source = 'cisa-kev'").fetchone()[0]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Automated GRC Risk Register",
        f"**Generated:** {now} | **Active CISA KEV Context:** {kev_count} tracked vulnerabilities\n",
        "| Risk ID | Asset (Env) | Finding | Score | Severity | SLA | NIST CSF | ISO 27001 | Remediation |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |"
    ]

    if not baselines:
        lines.append("| RSK-000 | None | No active port baselines recorded yet (run `python3 main.py scan <host>` first) | 0 | INFO | N/A | N/A | N/A | Run baseline scan |")
    else:
        for idx, (host, port, banner, _) in enumerate(baselines, start=1):
            meta = assets.get(host, {"name": host, "environment": "unclassified", "criticality": 3})
            score, severity, sla = calculate_risk_score(port, meta["criticality"], kev_count)
            title, nist, iso, fix = map_port_to_controls(port)
            risk_id = f"RSK-{idx:03d}"
            asset_label = f"`{host}` ({meta['name']} / {meta['environment']})"
            finding_label = f"Port `{port}`: {title}"
            lines.append(f"| **{risk_id}** | {asset_label} | {finding_label} | **{score}/25** | **{severity}** | {sla} | {nist} | {iso} | {fix} |")

    out_path = Path("reports/RISK_REGISTER.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[+] GRC Risk Register generated at {out_path} ({len(baselines)} findings scored).")

from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import init_db
from risk.compliance_mapper import map_port_to_controls

HIGH_RISK_PORTS = {21, 23, 3306, 5432, 6379, 9200}

CLOUD_SEVERITY_MAP = {
    "CRITICAL": ("22/25", "24 Hours", "NIST CSF PR.AC-3", "ISO 27001 A.8.9"),
    "HIGH": ("16/25", "7 Days", "NIST CSF PR.IP-1", "ISO 27001 A.8.9"),
    "MEDIUM": ("10/25", "30 Days", "NIST CSF DE.CM-7", "ISO 27001 A.8.20"),
    "LOW": ("4/25", "90 Days", "NIST CSF ID.RA-1", "ISO 27001 A.8.8"),
}

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

    raw_score = base_likelihood * criticality
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
    cloud_rows = conn.execute("SELECT finding_id, resource_file, severity, benchmark, description FROM cloud_findings ORDER BY severity, resource_file").fetchall()
    kev_count = conn.execute("SELECT COUNT(*) FROM threat_iocs WHERE source = 'cisa-kev'").fetchone()[0]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Automated GRC Risk Register (Network + Cloud Posture)",
        f"**Generated:** {now} | **Active CISA KEV Context:** {kev_count} tracked vulnerabilities\n",
        "| Risk ID | Asset / Resource | Finding | Score | Severity | SLA | NIST CSF | ISO 27001 | Remediation |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |"
    ]

    risk_idx = 1
    for host, port, banner, _ in baselines:
        meta = assets.get(host, {"name": host, "environment": "unclassified", "criticality": 3})
        score, severity, sla = calculate_risk_score(port, meta["criticality"], kev_count)
        title, nist, iso, fix = map_port_to_controls(port)
        lines.append(
            f"| **RSK-{risk_idx:03d}** | `{host}` ({meta['name']} / {meta['environment']}) | Port `{port}`: {title} | **{score}/25** | **{severity}** | {sla} | {nist} | {iso} | {fix} |"
        )
        risk_idx += 1

    for fid, res_file, severity, benchmark, desc in cloud_rows:
        score_str, sla, nist, iso = CLOUD_SEVERITY_MAP.get(severity, ("10/25", "30 Days", "NIST CSF PR.IP-1", "ISO 27001 A.8.9"))
        lines.append(
            f"| **RSK-{risk_idx:03d}** | `{res_file}` (Cloud IaC) | [{benchmark}] {desc} | **{score_str}** | **{severity}** | {sla} | {nist} | {iso} | Remediate per {benchmark} ({fid}). |"
        )
        risk_idx += 1

    if risk_idx == 1:
        lines.append("| RSK-000 | None | No active network or cloud findings recorded yet | 0 | INFO | N/A | N/A | N/A | Run `scan` or `cloud-audit` |")

    out_path = Path("reports/RISK_REGISTER.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[+] GRC Risk Register generated at {out_path} ({risk_idx - 1} total findings scored).")

import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import init_db
from risk.scorer import load_assets, calculate_risk_score
from risk.compliance_mapper import map_port_to_controls

def build_ecs_events() -> list:
    conn = init_db()
    assets = load_assets()
    baselines = conn.execute("SELECT host, port, banner, last_seen FROM port_baselines").fetchall()
    kev_count = conn.execute("SELECT COUNT(*) FROM threat_iocs WHERE source = 'cisa-kev'").fetchone()[0]
    now = datetime.now(timezone.utc).isoformat()

    events = []
    for host, port, banner, last_seen in baselines:
        meta = assets.get(host, {"name": host, "environment": "unclassified", "criticality": 3, "owner": "Unassigned"})
        score, severity, sla = calculate_risk_score(port, meta["criticality"], kev_count)
        title, nist, iso, fix = map_port_to_controls(port)

        events.append({
            "@timestamp": now,
            "ecs": {"version": "8.11.0"},
            "event": {
                "kind": "alert" if score >= 12 else "state",
                "category": ["network", "vulnerability"],
                "severity": score,
                "risk_score": score * 4,
            },
            "host": {"ip": host, "name": meta["name"], "environment": meta["environment"]},
            "destination": {"port": port},
            "service": {"name": title, "state": banner},
            "compliance": {"nist_csf": nist, "iso_27001": iso, "sla": sla, "remediation": fix},
        })
    return events

def ship_to_logstash(logstash_host: str = "127.0.0.1", logstash_port: int = 5044) -> None:
    events = build_ecs_events()
    out_ndjson = Path("data/ecs_telemetry.ndjson")
    out_ndjson.parent.mkdir(parents=True, exist_ok=True)
    with out_ndjson.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    print(f"[+] Exported {len(events)} Elastic Common Schema (ECS) events to {out_ndjson}")

    try:
        with socket.create_connection((logstash_host, logstash_port), timeout=3.0) as sock:
            for ev in events:
                sock.sendall((json.dumps(ev) + "\n").encode("utf-8"))
            print(f"[+] Shipped {len(events)} ECS events live to Logstash ({logstash_host}:{logstash_port})")
    except OSError:
        print(f"[*] Logstash listener not active on {logstash_host}:{logstash_port} (saved offline NDJSON ready for ingestion).")

if __name__ == "__main__":
    ship_to_logstash()

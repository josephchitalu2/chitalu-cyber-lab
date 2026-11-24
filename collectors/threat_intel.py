import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import init_db

SPAMHAUS_DROP_URL = "https://spamhaus.org"
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

def fetch_spamhaus_drop(conn) -> int:
    req = urllib.request.Request(SPAMHAUS_DROP_URL, headers={"User-Agent": "Mozilla/5.0 (ChitaluCyberLab)"})
    now = datetime.now(timezone.utc).isoformat()
    added = 0
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            for raw_line in resp.read().decode("utf-8", errors="ignore").splitlines():
                line = raw_line.split(";")[0].strip()
                if not line or "<" in line:
                    continue
                cur = conn.execute(
                    "INSERT OR IGNORE INTO threat_iocs (indicator, source, category, added_at) VALUES (?, ?, ?, ?)",
                    (line, "spamhaus-drop", "malicious-netblock", now)
                )
                added += cur.rowcount
        conn.commit()
    except Exception as e:
        print(f"[!] Warning: Spamhaus DROP fetch failed ({e})")
    return added

def fetch_cisa_kev(conn) -> int:
    now = datetime.now(timezone.utc).isoformat()
    added = 0
    try:
        req = urllib.request.Request(CISA_KEV_URL, headers={"User-Agent": "Mozilla/5.0 (ChitaluCyberLab)", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            for vuln in payload.get("vulnerabilities", [])[:50]:
                cve = vuln.get("cveID")
                vendor = vuln.get("vendorProject", "Unknown")
                if cve:
                    cur = conn.execute(
                        "INSERT OR IGNORE INTO threat_iocs (indicator, source, category, added_at) VALUES (?, ?, ?, ?)",
                        (cve, "cisa-kev", f"kev:{vendor}", now)
                    )
                    added += cur.rowcount
        conn.commit()
    except Exception as e:
        print(f"[!] Warning: CISA KEV fetch failed ({e})")
    return added

def export_ioc_snapshot(conn) -> None:
    out_file = Path("data/latest_iocs.txt")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    rows = conn.execute("SELECT indicator, source, category FROM threat_iocs ORDER BY added_at DESC LIMIT 200").fetchall()
    with out_file.open("w", encoding="utf-8") as f:
        f.write(f"# Chitalu Cyber Lab - Threat Intel Snapshot ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})\n")
        for ind, src, cat in rows:
            f.write(f"{ind}\t{src}\t{cat}\n")

if __name__ == "__main__":
    conn = init_db()
    new_ips = fetch_spamhaus_drop(conn)
    new_cves = fetch_cisa_kev(conn)
    export_ioc_snapshot(conn)
    total = conn.execute("SELECT COUNT(*) FROM threat_iocs").fetchone()[0]
    print(f"[+] Synced feeds: +{new_ips} Spamhaus DROP netblocks, +{new_cves} CISA KEVs (Total tracked: {total})")

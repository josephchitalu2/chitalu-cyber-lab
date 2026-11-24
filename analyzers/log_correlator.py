import re
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import init_db

IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def load_malicious_ips() -> dict:
    iocs = {}
    conn = init_db()
    for ind, src, cat in conn.execute("SELECT indicator, source, category FROM threat_iocs WHERE category LIKE '%ip%'").fetchall():
        iocs[ind] = f"{src} ({cat})"

    snapshot = Path("data/latest_iocs.txt")
    if snapshot.exists():
        for line in snapshot.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 3 and IPV4_PATTERN.fullmatch(parts[0]):
                iocs[parts[0]] = f"{parts[1]} ({parts[2]})"
    return iocs

def correlate_logs(log_filepath: str) -> None:
    path = Path(log_filepath)
    if not path.exists():
        print(f"[-] Log file not found: {log_filepath}")
        return

    malicious_ips = load_malicious_ips()
    ip_hits = Counter()
    ioc_matches = {}

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            for ip in IPV4_PATTERN.findall(line):
                ip_hits[ip] += 1
                if ip in malicious_ips:
                    ioc_matches[ip] = malicious_ips[ip]

    print(f"[*] Scanned {path} | Unique IPs seen: {len(ip_hits)} | Known Threat IoCs loaded: {len(malicious_ips)}")
    if ioc_matches:
        for ip, intel in ioc_matches.items():
            print(f"[CRITICAL IOC MATCH] {ip} seen {ip_hits[ip]} times -> {intel}")
    else:
        print("[+] Clean: No known C2 threat indicators matched in log file.")

if __name__ == "__main__":
    target_log = sys.argv[1] if len(sys.argv) > 1 else "/var/log/auth.log"
    correlate_logs(target_log)

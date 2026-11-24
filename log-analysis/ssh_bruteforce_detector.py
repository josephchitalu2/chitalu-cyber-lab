import re
import sys
from collections import Counter
from pathlib import Path

FAILED_PATTERN = re.compile(r"Failed password for (?:invalid user )?\S+ from (\d+\.\d+\.\d+\.\d+)")

def analyze_log(filepath: str, threshold: int = 5) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"[-] Log file not found: {filepath}")
        return

    counts = Counter()
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = FAILED_PATTERN.search(line)
            if match:
                counts[match.group(1)] += 1

    print(f"[*] Flagged IPs with >= {threshold} failed SSH attempts:")
    for ip, count in counts.most_common():
        if count >= threshold:
            print(f"[!] {ip:<16} -> {count} failed attempts")

if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else "/var/log/auth.log"
    analyze_log(log_path)

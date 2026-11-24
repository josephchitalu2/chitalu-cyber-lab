import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.database import init_db, record_and_diff_port

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8000, 8080, 8443]

def probe_port(host: str, port: int):
    try:
        with socket.create_connection((host, port), timeout=1.5) as sock:
            sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            raw = sock.recv(512).decode(errors="ignore").strip().splitlines()
            banner = raw[0][:80] if raw else "Open (no banner)"
            return (port, banner)
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None

def run_monitor(host: str) -> None:
    conn = init_db()
    print(f"[*] Running stateful drift scan on {host}...")
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(lambda p: probe_port(host, p), COMMON_PORTS))

    open_ports = [r for r in results if r is not None]
    if not open_ports:
        print(f"[-] No open ports detected on {host}.")
        return

    for port, banner in open_ports:
        alert = record_and_diff_port(conn, host, port, banner)
        print(alert)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    run_monitor(target)

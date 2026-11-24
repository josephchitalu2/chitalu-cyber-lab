import socket
import sys
from concurrent.futures import ThreadPoolExecutor

def scan_port(host: str, port: int) -> None:
    try:
        with socket.create_connection((host, port), timeout=1.5) as sock:
            sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = sock.recv(1024).decode(errors="ignore").strip().splitlines()
            first_line = banner[0] if banner else "No banner"
            print(f"[+] {host}:{port} OPEN | {first_line}")
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    common_ports = [21, 22, 25, 53, 80, 110, 143, 443, 445, 3306, 5432, 8080, 8443]
    print(f"[*] Scanning {target} across {len(common_ports)} common ports...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        for p in common_ports:
            executor.submit(scan_port, target, p)

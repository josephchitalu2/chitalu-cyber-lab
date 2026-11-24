import ssl
import socket
import sys
from datetime import datetime, timezone

def inspect_cert(hostname: str, port: int = 443) -> None:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=5.0) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            subject = dict(x[0] for x in cert.get("subject", []))
            issuer = dict(x[0] for x in cert.get("issuer", []))
            not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            days_left = (not_after - datetime.now(timezone.utc)).days

            print(f"[+] Target:      {hostname}:{port}")
            print(f"[+] Common Name: {subject.get('commonName')}")
            print(f"[+] Issuer:      {issuer.get('organizationName')} ({issuer.get('commonName')})")
            print(f"[+] Expires On:  {not_after.strftime('%Y-%m-%d')} ({days_left} days remaining)")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    inspect_cert(domain)

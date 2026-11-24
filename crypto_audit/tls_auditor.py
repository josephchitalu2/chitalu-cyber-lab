import ssl
import socket
import urllib.request
from datetime import datetime, timezone

def audit_tls_endpoint(hostname: str, port: int = 443) -> None:
    clean_host = hostname.replace("https://", "").replace("http://", "").split("/")
    context = ssl.create_default_context()

    try:
        with socket.create_connection((clean_host, port), timeout=6.0) as sock:
            with context.wrap_socket(sock, server_hostname=clean_host) as ssock:
                cert = ssock.getpeercert()
                protocol = ssock.version()
                cipher_name, _, cipher_bits = ssock.cipher()

                subject = dict(x for x in cert.get("subject", []))
                issuer = dict(x for x in cert.get("issuer", []))
                not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                days_left = (not_after - datetime.now(timezone.utc)).days

                print(f"[*] TLS & Cryptographic Posture Audit: {clean_host}:{port}")
                print(f"  [+] Common Name:    {subject.get('commonName')}")
                print(f"  [+] Issuer:         {issuer.get('organizationName')} ({issuer.get('commonName')})")
                print(f"  [+] Expiry:         {not_after.strftime('%Y-%m-%d')} ({days_left} days remaining)")
                print(f"  [+] Protocol:       {protocol}")
                print(f"  [+] Cipher Suite:   {cipher_name} ({cipher_bits}-bit)")

                if protocol in ("TLSv1", "TLSv1.1"):
                    print(f"  [HIGH | NIST SP 800-52] Deprecated protocol {protocol} negotiated.")
                if cipher_bits < 128:
                    print(f"  [CRITICAL | Weak Cipher] Key length {cipher_bits}-bit is below 128-bit minimum.")
                if days_left < 30:
                    print(f"  [MEDIUM | Cert Expiry] Certificate expires in {days_left} days.")
    except Exception as e:
        print(f"[!] TLS handshake failed for {clean_host}:{port} -> {e}")
        return

    try:
        req = urllib.request.Request(f"https://{clean_host}", method="HEAD", headers={"User-Agent": "ChitaluCyberLab"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            hsts = resp.headers.get("Strict-Transport-Security")
            if hsts:
                print(f"  [+] HSTS Enabled:   {hsts}")
            else:
                print("  [MEDIUM | OWASP A05] Missing Strict-Transport-Security (HSTS) header.")
    except Exception:
        pass

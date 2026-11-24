CONTROL_MAP = {
    "21": ("FTP Cleartext Service", "NIST CSF PR.DS-2", "ISO 27001 A.8.24", "Disable FTP; migrate to SFTP/SSH."),
    "22": ("SSH Remote Access", "NIST CSF PR.AC-4", "ISO 27001 A.8.5", "Enforce key-based auth and disable root login."),
    "23": ("Telnet Unencrypted Protocol", "NIST CSF PR.DS-2", "ISO 27001 A.8.24", "Immediately disable Telnet and replace with SSH."),
    "80": ("Unencrypted HTTP Endpoint", "NIST CSF PR.DS-2", "ISO 27001 A.8.24", "Enforce HTTPS/TLS 1.3 redirect with HSTS."),
    "443": ("HTTPS Web Service", "NIST CSF PR.IP-1", "ISO 27001 A.8.9", "Verify TLS cipher strength and certificate expiry."),
    "3306": ("Exposed MySQL Database", "NIST CSF PR.AC-5", "ISO 27001 A.8.20", "Bind database to localhost or private VPC subnet."),
    "5432": ("Exposed PostgreSQL Database", "NIST CSF PR.AC-5", "ISO 27001 A.8.20", "Restrict database port via firewall/security group."),
    "6379": ("Exposed Redis In-Memory Store", "NIST CSF PR.AC-3", "ISO 27001 A.8.3", "Require authentication and block external access."),
    "9200": ("Exposed Elasticsearch Node", "NIST CSF PR.AC-3", "ISO 27001 A.8.20", "Enable X-Pack security and restrict external HTTP API."),
}

def map_port_to_controls(port: int) -> tuple:
    return CONTROL_MAP.get(
        str(port),
        ("Unclassified Network Service", "NIST CSF DE.CM-7", "ISO 27001 A.8.9", "Review business justification and restrict via firewall.")
    )

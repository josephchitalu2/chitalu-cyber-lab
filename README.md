# Chitalu Cyber Lab

A modular collection of defensive security utilities, network reconnaissance scripts, and lab tooling built in Python.

## Structure
- **`recon/`**: Network discovery and service banner enumeration (`port_banner_scanner.py`).
- **`log-analysis/`**: Blue-team log parsing and anomaly detection (`ssh_bruteforce_detector.py`).
- **`crypto-audit/`**: SSL/TLS certificate inspection and configuration auditing (`tls_cert_inspector.py`).

## Usage
```bash
python3 recon/port_banner_scanner.py 127.0.0.1
python3 log-analysis/ssh_bruteforce_detector.py /var/log/auth.log
python3 crypto-audit/tls_cert_inspector.py example.com
```

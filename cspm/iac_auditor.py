import re
from pathlib import Path
from cspm.iam_analyzer import audit_iam_policy

AWS_KEY_PATTERN = re.compile(r"AKIA[0-9A-Z]{16}")

def audit_terraform(filepath: Path) -> list:
    findings = []
    content = filepath.read_text(encoding="utf-8", errors="ignore")

    if AWS_KEY_PATTERN.search(content):
        findings.append(f"[CRITICAL | CIS AWS 1.14] {filepath.name}: Hardcoded AWS Access Key ID detected in Terraform code.")

    if 'cidr_blocks' in content and '"0.0.0.0/0"' in content:
        if any(port in content for port in ["22", "3389", "5432", "3306"]):
            findings.append(f"[CRITICAL | CIS AWS 5.2] {filepath.name}: Sensitive management/DB port exposed to 0.0.0.0/0.")
        else:
            findings.append(f"[MEDIUM | CIS AWS 5.1] {filepath.name}: Security group allows unrestricted ingress from 0.0.0.0/0.")

    if 'resource "aws_s3_bucket"' in content and "aws_s3_bucket_server_side_encryption_configuration" not in content:
        findings.append(f"[HIGH | CIS AWS 2.1.1] {filepath.name}: S3 bucket missing default server-side encryption block.")

    if 'acl' in content and '"public-read"' in content:
        findings.append(f"[CRITICAL | CIS AWS 2.1.5] {filepath.name}: S3 bucket configured with public-read ACL.")

    return findings

def audit_dockerfile(filepath: Path) -> list:
    findings = []
    lines = [l.strip() for l in filepath.read_text(encoding="utf-8", errors="ignore").splitlines()]

    has_non_root_user = False
    for line in lines:
        if line.startswith("FROM ") and ":latest" in line:
            findings.append(f"[LOW | CIS Docker 4.7] {filepath.name}: Base image uses mutable ':latest' tag instead of pinned digest/version.")
        if line.startswith("USER "):
            user_val = line.split(None, 1)[1].strip().lower()
            if user_val not in ("root", "0"):
                has_non_root_user = True
        if any(secret in line.upper() for secret in ["AWS_SECRET_ACCESS_KEY=", "PASSWORD=", "API_KEY="]):
            findings.append(f"[CRITICAL | CIS Docker 4.10] {filepath.name}: Hardcoded secret in ENV/ARG instruction.")

    if not has_non_root_user:
        findings.append(f"[HIGH | CIS Docker 4.1] {filepath.name}: Container runs as root (no non-root USER instruction found).")

    return findings

def run_cspm_audit(target_dir: str = "cspm/lab_targets") -> int:
    root = Path(target_dir)
    if not root.exists():
        print(f"[-] Target path not found: {target_dir}")
        return 1

    all_findings = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix == ".tf":
            all_findings.extend(audit_terraform(path))
        elif path.suffix == ".json":
            all_findings.extend(audit_iam_policy(path))
        elif path.name == "Dockerfile" or path.name.startswith("Dockerfile."):
            all_findings.extend(audit_dockerfile(path))

    print(f"[*] CSPM & IaC Posture Audit completed on '{target_dir}' | Findings: {len(all_findings)}")
    for item in all_findings:
        print(f"  {item}")

    return len(all_findings)

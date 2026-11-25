# Automated GRC Risk Register (Network + Cloud Posture)
**Generated:** 2026-11-25 07:41 UTC | **Active CISA KEV Context:** 50 tracked vulnerabilities

| Risk ID | Asset / Resource | Finding | Score | Severity | SLA | NIST CSF | ISO 27001 | Remediation |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **RSK-001** | `cspm/lab_targets/Dockerfile` (Cloud IaC) | [CIS Docker 4.10] Dockerfile: Hardcoded secret in ENV/ARG instruction. | **22/25** | **CRITICAL** | 24 Hours | NIST CSF PR.AC-3 | ISO 27001 A.8.9 | Remediate per CIS Docker 4.10 (CSPM-2E1097360D). |
| **RSK-002** | `cspm/lab_targets/prod_vpc_s3.tf` (Cloud IaC) | [CIS AWS 5.2] prod_vpc_s3.tf: Sensitive management/DB port exposed to 0.0.0.0/0. | **22/25** | **CRITICAL** | 24 Hours | NIST CSF PR.AC-3 | ISO 27001 A.8.9 | Remediate per CIS AWS 5.2 (CSPM-C50E02D784). |
| **RSK-003** | `cspm/lab_targets/prod_vpc_s3.tf` (Cloud IaC) | [CIS AWS 2.1.5] prod_vpc_s3.tf: S3 bucket configured with public-read ACL. | **22/25** | **CRITICAL** | 24 Hours | NIST CSF PR.AC-3 | ISO 27001 A.8.9 | Remediate per CIS AWS 2.1.5 (CSPM-23D130BC83). |
| **RSK-004** | `cspm/lab_targets/Dockerfile` (Cloud IaC) | [CIS Docker 4.1] Dockerfile: Container runs as root (no non-root USER instruction found). | **16/25** | **HIGH** | 7 Days | NIST CSF PR.IP-1 | ISO 27001 A.8.9 | Remediate per CIS Docker 4.1 (CSPM-D8D2F5DB01). |
| **RSK-005** | `cspm/lab_targets/ci_deploy_iam_policy.json` (Cloud IaC) | [CIS AWS 1.15] ci_deploy_iam_policy.json (Stmt #1): Unscoped privilege-escalation vector 'iam:PassRole' on '*' without Conditions. | **16/25** | **HIGH** | 7 Days | NIST CSF PR.IP-1 | ISO 27001 A.8.9 | Remediate per CIS AWS 1.15 (CSPM-19F509D6DB). |
| **RSK-006** | `cspm/lab_targets/prod_vpc_s3.tf` (Cloud IaC) | [CIS AWS 2.1.1] prod_vpc_s3.tf: S3 bucket missing default server-side encryption block. | **16/25** | **HIGH** | 7 Days | NIST CSF PR.IP-1 | ISO 27001 A.8.9 | Remediate per CIS AWS 2.1.1 (CSPM-E4D048D3C5). |
| **RSK-007** | `cspm/lab_targets/Dockerfile` (Cloud IaC) | [CIS Docker 4.7] Dockerfile: Base image uses mutable ':latest' tag instead of pinned digest/version. | **4/25** | **LOW** | 90 Days | NIST CSF ID.RA-1 | ISO 27001 A.8.8 | Remediate per CIS Docker 4.7 (CSPM-6B011A5BF2). |
| **RSK-008** | `cspm/lab_targets/ci_deploy_iam_policy.json` (Cloud IaC) | [Least-Privilege] ci_deploy_iam_policy.json (Stmt #1): Wildcard service permission 'ec2:*' across all resources. | **10/25** | **MEDIUM** | 30 Days | NIST CSF DE.CM-7 | ISO 27001 A.8.20 | Remediate per Least-Privilege (CSPM-9F4615EF24). |

import hashlib
import os
import urllib.request
from core.database import init_db, save_cloud_finding

LOCALSTACK_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://127.0.0.1:4566")

def _persist_live_finding(conn, resource_arn: str, severity: str, benchmark: str, desc: str) -> str:
    digest = hashlib.sha256(f"{resource_arn}:{desc}".encode("utf-8")).hexdigest()[:10]
    fid = f"AWS-LIVE-{digest.upper()}"
    save_cloud_finding(conn, fid, resource_arn, severity, benchmark, desc)
    return f"  [{severity} | {benchmark}] {resource_arn}: {desc}"

def audit_live_aws(endpoint_url: str = LOCALSTACK_ENDPOINT) -> None:
    try:
        urllib.request.urlopen(endpoint_url, timeout=2.5)
    except Exception:
        print(f"[-] LocalStack / AWS endpoint unreachable at {endpoint_url}.")
        print("[*] Start local AWS emulation with: docker compose -f cspm/docker-compose.localstack.yml up -d")
        return

    try:
        import boto3
    except ImportError:
        print("[-] 'boto3' is not installed. Install it via 'pip install boto3' or 'sudo pacman -S python-boto3' to run live API audits.")
        return

    conn = init_db()
    creds = {"endpoint_url": endpoint_url, "region_name": "us-east-1", "aws_access_key_id": "test", "aws_secret_access_key": "test"}
    s3 = boto3.client("s3", **creds)
    iam = boto3.client("iam", **creds)
    ec2 = boto3.client("ec2", **creds)

    alerts = []

    for bucket in s3.list_buckets().get("Buckets", []):
        name = bucket["Name"]
        arn = f"arn:aws:s3:::{name}"
        acl = s3.get_bucket_acl(Bucket=name)
        for grant in acl.get("Grants", []):
            uri = grant.get("Grantee", {}).get("URI", "")
            if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                alerts.append(_persist_live_finding(conn, arn, "CRITICAL", "CIS AWS 2.1.5", f"Live S3 bucket '{name}' grants public access via ACL."))
        try:
            s3.get_bucket_encryption(Bucket=name)
        except Exception:
            alerts.append(_persist_live_finding(conn, arn, "HIGH", "CIS AWS 2.1.1", f"Live S3 bucket '{name}' lacks default server-side encryption."))

    for sg in ec2.describe_security_groups().get("SecurityGroups", []):
        sg_id = sg["GroupId"]
        arn = f"arn:aws:ec2:us-east-1:000000000000:security-group/{sg_id}"
        for perm in sg.get("IpPermissions", []):
            from_p = perm.get("FromPort", 0)
            to_p = perm.get("ToPort", 65535)
            for ip_range in perm.get("IpRanges", []):
                if ip_range.get("CidrIp") == "0.0.0.0/0":
                    if any(p in range(from_p, to_p + 1) for p in (22, 3389, 5432, 3306)):
                        alerts.append(_persist_live_finding(conn, arn, "CRITICAL", "CIS AWS 5.2", f"Security Group {sg_id} exposes port {from_p}-{to_p} to 0.0.0.0/0."))

    for pol in iam.list_policies(Scope="Local").get("Policies", []):
        arn = pol["Arn"]
        ver = iam.get_policy_version(PolicyArn=arn, VersionId=pol["DefaultVersionId"])
        stmts = ver["PolicyVersion"]["Document"].get("Statement", [])
        if isinstance(stmts, dict):
            stmts = [stmts]
        for stmt in stmts:
            if stmt.get("Effect") == "Allow" and stmt.get("Action") == "*" and stmt.get("Resource") == "*":
                alerts.append(_persist_live_finding(conn, arn, "CRITICAL", "CIS AWS 1.16", f"Customer IAM policy '{pol['PolicyName']}' grants full AdministratorAccess (*:*)."))

    print(f"[*] Live AWS API Posture Audit ({endpoint_url}) | Findings persisted: {len(alerts)}")
    for line in alerts:
        print(line)

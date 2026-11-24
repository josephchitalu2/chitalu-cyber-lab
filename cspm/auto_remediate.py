import os
import urllib.request

LOCALSTACK_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://127.0.0.1:4566")

def remediate_live_aws(endpoint_url: str = LOCALSTACK_ENDPOINT) -> None:
    try:
        urllib.request.urlopen(f"{endpoint_url}/_localstack/health", timeout=2.5)
    except Exception:
        print(f"[-] LocalStack / AWS endpoint unreachable at {endpoint_url}.")
        print("[*] Start local AWS emulation with: docker compose -f cspm/docker-compose.localstack.yml up -d")
        return

    try:
        import boto3
    except ImportError:
        print("[-] 'boto3' is not installed. Install it via 'sudo pacman -S python-boto3' to run auto-remediation.")
        return

    creds = {"endpoint_url": endpoint_url, "region_name": "us-east-1", "aws_access_key_id": "test", "aws_secret_access_key": "test"}
    s3 = boto3.client("s3", **creds)
    ec2 = boto3.client("ec2", **creds)

    actions_taken = 0

    # 1. Enforce Private ACL & AES256 Default Encryption on all S3 Buckets
    for bucket in s3.list_buckets().get("Buckets", []):
        name = bucket["Name"]
        s3.put_bucket_acl(Bucket=name, ACL="private")
        s3.put_bucket_encryption(
            Bucket=name,
            ServerSideEncryptionConfiguration={
                "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
            },
        )
        print(f"[REMEDIATED | CIS AWS 2.1.1 & 2.1.5] Enforced 'private' ACL and AES256 encryption on S3 bucket '{name}'.")
        actions_taken += 1

    # 2. Revoke 0.0.0.0/0 Ingress on Sensitive Management/DB Ports (22, 3389, 5432, 3306)
    for sg in ec2.describe_security_groups().get("SecurityGroups", []):
        sg_id = sg["GroupId"]
        for perm in sg.get("IpPermissions", []):
            from_p = perm.get("FromPort", 0)
            to_p = perm.get("ToPort", 65535)
            has_open_cidr = any(r.get("CidrIp") == "0.0.0.0/0" for r in perm.get("IpRanges", []))
            if has_open_cidr and any(p in range(from_p, to_p + 1) for p in (22, 3389, 5432, 3306)):
                ec2.revoke_security_group_ingress(GroupId=sg_id, IpPermissions=[perm])
                print(f"[REMEDIATED | CIS AWS 5.2] Revoked 0.0.0.0/0 ingress on port {from_p}-{to_p} from Security Group '{sg_id}'.")
                actions_taken += 1

    print(f"[*] Live Cloud Auto-Remediation complete | Total fixes applied: {actions_taken}")

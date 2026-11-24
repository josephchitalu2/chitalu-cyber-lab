import json
import os
import urllib.request

LOCALSTACK_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://127.0.0.1:4566")

def seed_vulnerable_resources(endpoint_url: str = LOCALSTACK_ENDPOINT) -> None:
    try:
        urllib.request.urlopen(endpoint_url, timeout=2.5)
    except Exception:
        print(f"[-] LocalStack not running at {endpoint_url}. Start it with:")
        print("    docker compose -f cspm/docker-compose.localstack.yml up -d")
        return

    import boto3
    creds = {"endpoint_url": endpoint_url, "region_name": "us-east-1", "aws_access_key_id": "test", "aws_secret_access_key": "test"}
    s3 = boto3.client("s3", **creds)
    iam = boto3.client("iam", **creds)
    ec2 = boto3.client("ec2", **creds)

    # 1. Create public, unencrypted S3 bucket
    bucket_name = "chitalu-live-unencrypted-exports"
    try:
        s3.create_bucket(Bucket=bucket_name, ACL="public-read")
        print(f"[+] Seeded public S3 bucket: {bucket_name}")
    except Exception as e:
        print(f"[*] S3 bucket note: {e}")

    # 2. Create overly permissive IAM Policy (*:*)
    policy_doc = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]
    })
    try:
        iam.create_policy(PolicyName="ChitaluWildcardAdminPolicy", PolicyDocument=policy_doc)
        print("[+] Seeded wildcard IAM policy: ChitaluWildcardAdminPolicy")
    except Exception as e:
        print(f"[*] IAM policy note: {e}")

    # 3. Create EC2 Security Group exposing SSH (22) to 0.0.0.0/0
    try:
        sg = ec2.create_security_group(GroupName="chitalu-open-ssh-sg", Description="Insecure SSH ingress")
        ec2.authorize_security_group_ingress(
            GroupId=sg["GroupId"],
            IpPermissions=[{"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]
        )
        print(f"[+] Seeded open EC2 Security Group: {sg['GroupId']} (port 22 -> 0.0.0.0/0)")
    except Exception as e:
        print(f"[*] EC2 SG note: {e}")

if __name__ == "__main__":
    seed_vulnerable_resources()

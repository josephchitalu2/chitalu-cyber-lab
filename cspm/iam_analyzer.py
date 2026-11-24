import json
from pathlib import Path

PRIVESC_ACTIONS = {
    "iam:PassRole",
    "iam:CreatePolicyVersion",
    "iam:SetDefaultPolicyVersion",
    "iam:AttachUserPolicy",
    "iam:AttachRolePolicy",
    "iam:PutUserPolicy",
    "sts:AssumeRole",
}

def audit_iam_policy(filepath: Path) -> list:
    findings = []
    try:
        doc = json.loads(filepath.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"[ERROR] Failed to parse {filepath}: {e}"]

    statements = doc.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]

    for idx, stmt in enumerate(statements, start=1):
        if stmt.get("Effect") != "Allow":
            continue

        actions = stmt.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        resources = stmt.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        has_wildcard_resource = "*" in resources
        has_conditions = bool(stmt.get("Condition"))

        if "*" in actions and has_wildcard_resource:
            findings.append(
                f"[CRITICAL | CIS AWS 1.16] {filepath.name} (Stmt #{idx}): Full AdministratorAccess ('Action': '*', 'Resource': '*')."
            )

        for act in actions:
            if act in PRIVESC_ACTIONS and has_wildcard_resource and not has_conditions:
                findings.append(
                    f"[HIGH | CIS AWS 1.15] {filepath.name} (Stmt #{idx}): Unscoped privilege-escalation vector '{act}' on '*' without Conditions."
                )
            elif act.endswith(":*") and has_wildcard_resource:
                findings.append(
                    f"[MEDIUM | Least-Privilege] {filepath.name} (Stmt #{idx}): Wildcard service permission '{act}' across all resources."
                )

    return findings

import unittest
from pathlib import Path
from risk.scorer import calculate_risk_score
from cspm.iam_analyzer import audit_iam_policy
from cspm.iac_auditor import audit_terraform, audit_dockerfile

class TestSecurityEngines(unittest.TestCase):
    def test_risk_scoring_critical_threshold(self):
        score, severity, sla = calculate_risk_score(port=5432, criticality=5, active_kev_count=10)
        self.assertEqual(score, 20)
        self.assertEqual(severity, "CRITICAL")
        self.assertEqual(sla, "24 Hours")

    def test_cspm_lab_targets_detection(self):
        iam_findings = audit_iam_policy(Path("cspm/lab_targets/ci_deploy_iam_policy.json"))
        tf_findings = audit_terraform(Path("cspm/lab_targets/prod_vpc_s3.tf"))
        docker_findings = audit_dockerfile(Path("cspm/lab_targets/Dockerfile"))

        self.assertGreaterEqual(len(iam_findings), 2)
        self.assertGreaterEqual(len(tf_findings), 3)
        self.assertGreaterEqual(len(docker_findings), 3)

if __name__ == "__main__":
    unittest.main()

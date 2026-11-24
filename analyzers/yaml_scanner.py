import sys
import urllib.request
import urllib.error
from pathlib import Path

def parse_simple_yaml(filepath: Path) -> dict:
    data = {}
    for raw in filepath.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip().strip('"').strip("'")
        if val:
            data[key.strip()] = val
    return data

def run_templates(base_url: str, template_dir: str = "templates") -> None:
    base = base_url.rstrip("/")
    if not base.startswith(("http://", "https://")):
        base = "http://" + base

    templates = sorted(Path(template_dir).glob("*.yaml"))
    print(f"[*] Running {len(templates)} YAML signatures against {base}...")

    for tpl_path in templates:
        rule = parse_simple_yaml(tpl_path)
        rule_id = rule.get("id", tpl_path.stem)
        severity = rule.get("severity", "info").upper()
        req_path = rule.get("path", "/")
        matcher = rule.get("match", "")
        target = f"{base}{req_path}"

        try:
            req = urllib.request.Request(target, headers={"User-Agent": "ChitaluCyberLab-Scanner/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                if matcher and matcher in body:
                    print(f"[VULN - {severity}] {rule_id} matched at {target}")
                else:
                    print(f"[-] {rule_id}: not vulnerable (HTTP {resp.status})")
        except urllib.error.HTTPError as e:
            print(f"[-] {rule_id}: HTTP {e.code}")
        except Exception as e:
            print(f"[!] {rule_id}: request failed ({e})")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    run_templates(url)

import subprocess
import json
from pathlib import Path

ECHIDNA_IMAGE = "ghcr.io/crytic/echidna/echidna:latest"


def run_echidna(contract_path, report_dir="reports"):
    contract_path = Path(contract_path).resolve()
    report_dir = Path(report_dir).resolve()
    report_dir.mkdir(exist_ok=True)

    output_file = report_dir / "echidna.json"

    # Ensure path is inside project root (for Docker mount)
    project_root = Path.cwd()
    relative_contract = contract_path.relative_to(project_root)

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{project_root}:/src",
        ECHIDNA_IMAGE,
        "echidna-test",
        f"/src/{relative_contract}",
        "--config", "/src/echidna.yaml",
        "--format", "json",
        "--output", "/src/reports/echidna.json"
    ]

    print("[ECHIDNA] Running Echidna fuzzing...")

    # IMPORTANT: Echidna exits non-zero when it finds issues or no properties
    subprocess.run(cmd, check=False)

    if output_file.exists():
        try:
            with open(output_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[ECHIDNA] Failed to parse JSON output")

    print("[ECHIDNA] No findings or no properties detected")
    return {}


def simplify_echidna_issues(echidna_data):
    """
    Convert raw Echidna JSON into HySCAV unified issue format
    """
    issues = []

    if not echidna_data:
        return issues

    for test_name, test_data in echidna_data.items():
        if test_data.get("status") == "failed":
            issues.append({
                "tool": "Echidna",
                "type": "Property Violation",
                "description": f"Echidna property failed: {test_name}",
                "severity": "High",
                "contract": test_data.get("contract", "Unknown")
            })

    return issues

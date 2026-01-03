import subprocess
import json


def run_mythril(contract_path):
    print("[MYTHRIL] Running symbolic execution...")

    command = [
        "myth",
        "analyze",
        contract_path,
        "--execution-timeout",
        "60",
        "--output",
        "json"
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    if not result.stdout:
        print("[MYTHRIL] No issues detected")
        return {
            "issues": [],
            "count": 0
        }

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("[MYTHRIL][ERROR] Failed to parse output")
        return None

    issues = data.get("issues", [])

    print(f"[MYTHRIL] Issues found: {len(issues)}")

    return {
        "issues": issues,
        "count": len(issues)
    }

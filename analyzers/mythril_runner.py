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
        return {"issues": []}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("[MYTHRIL][ERROR] Failed to parse output")
        return {"issues": []}

    issues = data.get("issues", [])
    print(f"[MYTHRIL] Issues found: {len(issues)}")

    return {"issues": issues}


def simplify_mythril_issues(mythril_result):
    simplified = []

    for i in mythril_result.get("issues", []):
        simplified.append({
            "tool": "mythril",
            "title": i.get("title"),
            "severity": i.get("severity"),
            "contract": i.get("contract"),
            "function": i.get("function"),
            "line": i.get("lineno"),
            "swc-id": i.get("swc-id"),
            "description": i.get("description")
        })

    return simplified

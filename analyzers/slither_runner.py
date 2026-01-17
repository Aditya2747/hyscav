import subprocess
import json
import os
import tempfile
import uuid


def run_slither(contract_path):
    print("[SLITHER] Running static analysis...")

    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(
        temp_dir, f"slither_{uuid.uuid4().hex}.json"
    )

    command = [
        "slither",
        contract_path,
        "--json",
        output_file,
        "--disable-color"
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )

    if not os.path.exists(output_file):
        print("[SLITHER][ERROR] Slither did not produce JSON output")
        return None

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[SLITHER][ERROR] JSON read failed: {e}")
        data = None
    finally:
        os.remove(output_file)

    print("[SLITHER] Analysis completed")
    return data


def simplify_slither_issues(slither_data):
    if not slither_data:
        return []

    issues = []

    detectors = slither_data.get("results", {}).get("detectors", [])

    for detector in detectors:
        element = detector.get("elements", [{}])[0]
        source_map = element.get("source_mapping", {})

        issues.append({
            "tool": "slither",
            "title": detector.get("check"),
            "severity": detector.get("impact"),
            "contract": element.get("contract"),
            "function": element.get("name"),
            "line": source_map.get("lines"),
            "description": detector.get("description")
        })

    return issues

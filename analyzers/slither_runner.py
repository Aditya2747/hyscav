import subprocess
import json
import os
import tempfile
import uuid


def run_slither(contract_path):
    print("[SLITHER] Running static analysis...")

    # Generate a unique JSON path WITHOUT creating the file
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"slither_{uuid.uuid4().hex}.json")

    command = [
        "slither",
        contract_path,
        "--json",
        output_file
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Slither reports findings via STDERR
    if result.stderr:
        print("[SLITHER][STDERR]")
        print(result.stderr)

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

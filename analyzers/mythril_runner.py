"""Mythril Native Runner (no Docker)."""

def run_mythril(contract_path: str):
    print("[MYTHRIL] Skip - pip install mythril[all]")
    return {"issues": []}

def simplify_mythril

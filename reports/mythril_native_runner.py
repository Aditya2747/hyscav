"""Native Mythril Runner (no Docker)."""

from mythril.cli import main
import sys
import json
from typing import Dict, Any

def run_mythril_native(contract_path: str) -> Dict[str, Any]:
    try:
        # Redirect myth output to capture JSON
        sys.argv = ['mythril', 'analyze', contract_path, '-o', 'json']
        # Capture stdout (mythril prints JSON)
        import io
        old_stdout = sys.stdout
        sys.stdout = captured = io.StringIO()
        main()
        sys.stdout = old_stdout
        
        output = captured.getvalue()
        data = json.loads(output.strip()) if output.strip() else {"issues": []}
        print(f"[MYTHRIL-NATIVE] Found {len(data.get('issues', []))} issues")
        return data
    except Exception as e:
        print(f"[MYTHRIL-NATIVE] Failed: {e}")
        return {"issues": []}

if __name__ == "__main__":
    import sys
    data = run_mythril_native(sys.argv[1]) if len(sys.argv) > 1 else {"issues": []}
    print(json.dumps(data, indent=2))


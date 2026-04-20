"""Mythril Docker Runner."""

import subprocess
import json
import os
from typing import Dict, Any, List

def run_mythril(contract_path: str) -> Dict[str, Any]:
    project_dir = os.getcwd()
    
    command = [
        "docker", "run", "--rm",
        "-v", f"{project_dir}:/tmp",
"mythril/myth",
        "analyze", "/tmp/" + os.path.basename(contract_path),
        "--execution-timeout", "60"
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"[MYTHRIL] Error: {result.stderr[:200]}")
            return {"issues": []}
        
        data = {"issues": []}
        try:
            if result.stdout.strip():
                data = json.loads(result.stdout)
        except:
            pass
        
        print(f"[MYTHRIL] Found {len(data.get('issues', []))} issues")
        return data
        
    except Exception as e:
        print(f"[MYTHRIL] Skip: {str(e)}")
        return {"issues": []}

def simplify_mythril_issues(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues = []
    for issue in data.get('issues', []):
        issues.append({
            'tool': 'Mythril',
            'title': issue.get('title', 'Mythril issue'),
            'severity': issue.get('severity', 'medium'),
            'description': issue.get('description', ''),
            'location': str(issue.get('location', ''))
        })
    return issues

if __name__ == "__main__":
    import sys
    data = run_mythril(sys.argv[1]) if len(sys.argv) > 1 else {"issues": []}
    print(json.dumps(data, indent=2))

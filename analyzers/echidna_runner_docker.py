"""Echidna Docker Runner."""

import subprocess
import json
import os
from typing import Dict, Any, List

def run_echidna(contract_path: str) -> Dict[str, Any]:
    project_dir = os.getcwd()
    tmp = 'tmp.sol'
    open(tmp, 'w').write(open(contract_path, 'r').read())
    
    command = [
        "docker", "run", "--rm",
        "-v", f"{project_dir}:/tmp",
"echidna/echidna:latest"
        "/tmp/" + os.path.basename(tmp),
        "--contract", os.path.splitext(os.path.basename(contract_path))[0],
        "--test-limit", "500"
    ]
    
    data = {}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        for line in result.stdout.split('\n'):
            if '!' in line and 'test_' in line:
                test = line.split('[')[0].strip()
                data[test] = {'status': 'failed'}
        print(f"[ECHIDNA] {len(data)} fails")
    except:
        pass
    
    return data

def simplify_echidna_issues(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues = []
    for test in data:
        issues.append({
            'tool': 'Echidna',
            'title': test,
            'severity': 'high',
            'description': 'Fuzz fail'
        })
    return issues

if __name__ == "__main__":
    import sys
    print(json.dumps(run_echidna(sys.argv[1]) if len(sys.argv) > 1 else {}, indent=2))


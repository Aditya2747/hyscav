import subprocess
import json
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

console = Console()

MYTHRIL_CATEGORY_MAP = {
    "Reentrancy": "reentrancy",
    "Integer Overflow and Underflow": "integer_overflow",
    "Access Control": "access_control",
    "Timestamp Dependency": "timestamp_dependence",
    "Unhandled Exception": "unchecked_calls",
    "Use of tx.origin": "tx_origin",
    "Dangerous Delegatecall": "short_address",
    # Add more
}

class MythrilRunner:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results_file = self.results_dir / "mythril_results.json"
    
    def run_mythril(self, sol_file: str) -> Dict[str, Any]:
        cmd = ["myth", "analyze", sol_file, "-o", "json"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            myth_json = json.loads(result.stdout)
            
            results = {
                "contract": Path(sol_file).stem,
                "issues": []
            }
            
            for issue in myth_json.get("issues", []):
                category = MYTHRIL_CATEGORY_MAP.get(issue.get("title", ""), "other")
                results["issues"].append({
                    "category": category,
                    "severity": issue.get("severity", "unknown"),
                    "lines": issue.get("line", []),
                    "description": issue["description"]
                })
            
            console.print(f"[green]✓ Mythril: {len(results['issues'])} issues[/green]")
            return results
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            console.print(f"[red]✗ Mythril failed on {sol_file}: {e}[/red]")
            return {"contract": Path(sol_file).stem, "issues": [], "error": str(e)}
    
    def run_all(self, contracts_dir: str = "contracts"):
        results = []
        for sol_file in Path(contracts_dir).glob("*.sol"):
            result = self.run_mythril(str(sol_file))
            results.append(result)
        
        self.results_file.write_text(json.dumps(results, indent=2))
        console.print(f"[green]Mythril results saved to {self.results_file}[/green]")


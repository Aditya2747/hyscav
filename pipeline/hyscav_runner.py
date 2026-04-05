import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

console = Console()

class HySCAVRunner:
    def __init__(self, results_dir: str = "results", hy_scav_dir: str = ".."):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results_file = self.results_dir / "hyscav_results.json"
        self.hy_scav_dir = Path(hy_scav_dir)
    
    def parse_hyscav_output(self, output: str) -> Dict[str, Any]:
        results = {"contract": "", "issues": [], "risk_score": 0.0, "risk_level": "LOW"}
        
        # Parse risk level/score from ML output
        if "Risk Level:" in output:
            lines = output.split('\n')
            for line in lines:
                if "Risk Level:" in line:
                    parts = line.split('(')
                    results["risk_level"] = parts[0].split(':')[1].strip()
                    if ')' in parts[1]:
                        results["risk_score"] = float(parts[1].split('=')[1].split(')')[0])
        
        # Parse Slither issues (since hy-scav runs Slither first)
        if "[SLITHER] Issues found:" in output:
            num_issues = int(output.split("[SLITHER] Issues found:")[1].split()[0])
            results["total_slither_issues"] = num_issues
        
        # Add vulnerability categories from issues (basic parsing)
        vulns = []
        if "reentrancy" in output.lower():
            vulns.append("reentrancy")
        if "overflow" in output.lower():
            vulns.append("integer_overflow")
        # Extend parser
        
        results["issues"] = vulns
        return results
    
    def run_hyscav(self, sol_file: str) -> Dict[str, Any]:
        cmd = ["python", "main.py", "analyze", sol_file]
        try:
            result = subprocess.run(cmd, cwd=self.hy_scav_dir, capture_output=True, text=True, timeout=120)
            console.print(f"[green]✓ hy-scav on {sol_file}[/green]")
            
            return self.parse_hyscav_output(result.stdout)
        except subprocess.TimeoutExpired:
            console.print(f"[red]✗ hy-scav timeout on {sol_file}[/red]")
            return {"contract": Path(sol_file).stem, "issues": [], "error": "timeout"}
        except Exception as e:
            console.print(f"[red]✗ hy-scav error on {sol_file}: {e}[/red]")
            return {"contract": Path(sol_file).stem, "issues": [], "error": str(e)}
    
    def run_all(self, contracts_dir: str = "contracts"):
        results = []
        for sol_file in Path(contracts_dir).glob("*.sol"):
            result = self.run_hyscav(str(sol_file))
            results.append(result)
        
        self.results_file.write_text(json.dumps(results, indent=2))
        console.print(f"[green]hy-scav results saved[/green]")


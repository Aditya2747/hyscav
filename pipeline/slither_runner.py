import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console

console = Console()

SLITHER_DETECTOR_MAP = {
    "reentrancy-no-eth": "reentrancy",
    "reentrancy-eth": "reentrancy",
    "arithmetic-packed-array": "integer_overflow",
    "unchecked-transfer": "unchecked_calls",
    "tx-origin": "tx_origin",
    "timestamp": "timestamp_dependence",
    "uninitialized-storage": "uninitialized_storage",
    "delegatecall": "short_address",  # approximate
    "suicidal": "access_control",
    # Add more mappings as needed
}

class SlitherRunner:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results_file = self.results_dir / "slither_results.json"
    
    def run_slither(self, sol_file: str) -> Dict[str, Any]:
        cmd = ["slither", sol_file, "--json", "-"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
            slither_json = json.loads(result.stdout)
            
            results = {
                "contract": Path(sol_file).stem,
                "issues": []
            }
            
            for detector in slither_json.get("detectors", []):
                category = SLITHER_DETECTOR_MAP.get(detector["check"], "other")
                issue = {
                    "category": category,
                    "impact": detector["impact"],
                    "confidence": detector["confidence"],
                    "lines": [check["location"]["start_line"] for check in detector["check"]],
                    "description": detector["description"]
                }
                results["issues"].append(issue)
            
            console.print(f"[green]✓ Slither: {len(results['issues'])} issues[/green]")
            return results
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            console.print(f"[red]✗ Slither failed on {sol_file}: {e}[/red]")
            return {"contract": Path(sol_file).stem, "issues": [], "error": str(e)}
    
    def run_all(self, contracts_dir: str = "contracts"):
        results = []
        for sol_file in Path(contracts_dir).glob("*.sol"):
            result = self.run_slither(str(sol_file))
            results.append(result)
        
        self.results_file.write_text(json.dumps(results, indent=2))
        console.print(f"[green]Slither results saved to {self.results_file}[/green]")


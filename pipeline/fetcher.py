import os
import json
import requests
import git
from pathlib import Path
from rich.console import Console

console = Console()

class ContractFetcher:
    def __init__(self, contracts_dir: str = "contracts", etherscan_key: str = None):
        self.contracts_dir = Path(contracts_dir)
        self.metadata_file = self.contracts_dir / "metadata.json"
        self.contracts_dir.mkdir(exist_ok=True)
        self.metadata = {"contracts": []}
        self.etherscan_key = etherscan_key

    def fetch_etherscan_verified(self, limit: int = 10):
        console.print("[yellow]Fetching Etherscan verified contracts...[/yellow]")
        
        url = "https://api.etherscan.io/api"
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "apikey": self.etherscan_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] != "1":
            console.print(f"[red]Etherscan API error: {data['message']}[/red]")
            return
        
        for contract_info in data["result"][:limit]:
            contract_name = contract_info["ContractName"]
            source_code = contract_info["SourceCode"]
            
            # Save contract
            sol_path = self.contracts_dir / f"{contract_name}.sol"
            sol_path.write_text(source_code)
            
            self.metadata["contracts"].append({
                "name": contract_name,
                "address": contract_info["ContractAddress"],
                "source_code": source_code,
                "verified": True,
                "known_vulns": []  
            })
        
        console.print(f"[green]Saved {len(data['result'][:limit])} Etherscan contracts[/green]")
    
    def fetch_smartbugs_curated(self):
        console.print("[yellow]Fetching SmartBugs Curated dataset...[/yellow]")
        
        smartbugs_dir = Path("smartbugs-curated")
        if not smartbugs_dir.exists():
            git.Repo.clone_from("https://github.com/smartbugs/smartbugs-curated.git", smartbugs_dir)
        
        # Parse vulnerabilities.json
        vulns_file = smartbugs_dir / "vulnerabilities.json"
        with open(vulns_file) as f:
            vulns_data = json.load(f)
        
        # Copy .sol files
        saved_count = 0
        for vuln_entry in vulns_data:
            sc_id = vuln_entry["smartcontract_id"]
            sol_path_src = smartbugs_dir / sc_id / f"{sc_id}.sol"
            if sol_path_src.exists():
                sol_path_dest = self.contracts_dir / f"smartbugs_{sc_id}.sol"
                sol_path_dest.write_text(sol_path_src.read_text())
                
                known_vulns = vuln_entry.get("vulnerability", [])
                self.metadata["contracts"].append({
                    "name": f"smartbugs_{sc_id}",
                    "source": "SmartBugs Curated",
                    "known_vulns": known_vulns,
                    "verified": False
                })
                saved_count += 1
        
        console.print(f"[green]Saved {saved_count} SmartBugs contracts[/green]")
    
    def save_metadata(self):
        self.metadata_file.write_text(json.dumps(self.metadata, indent=2))
        console.print(f"[green]Metadata saved to {self.metadata_file}[/green]")
    
    def run(self):
        self.fetch_smartbugs_curated()
        if self.etherscan_key:
            self.fetch_etherscan_verified(10)
        self.save_metadata()

if __name__ == "__main__":
    f = ContractFetcher()
    f.run()


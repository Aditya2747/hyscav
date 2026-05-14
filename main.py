import logging
import sys
import os
import subprocess
from typing import List, Dict, Any, Optional

from analyzers.slither_runner import run_slither, simplify_slither_issues
from analyzers.mythril_runner_docker import run_mythril, simplify_mythril_issues
from analyzers.echidna_runner_docker import run_echidna, simplify_echidna_issues

from controller.feature_extractor import extract_slither_features
from controller.decision_engine import decide_next_stage
from controller.merger import merge_issues

from ml.risk_model import predict_risk
from reports.report_generator import generate_report


logging.basicConfig(level=logging.INFO, format="%(message)s", force=True, encoding='utf-8', errors='replace')
logger = logging.getLogger("HySCAV")


def check_tools() -> Dict[str, bool]:
    """Check if required tools are installed."""
    tools = {
        "slither": False,
        "docker": False,
    }
    
    try:
        result = subprocess.run(
            ["slither", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        tools["slither"] = result.returncode == 0
    except:
        pass
    try:
        result = subprocess.run(
            ["docker", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        tools["docker"] = result.returncode == 0
    except:
        pass
    
    return tools


def main(contract_path: str) -> bool:

    try:
        # -------------------------------
        # Validate input
        # -------------------------------
        if not contract_path.endswith(".sol"):
            raise ValueError("Input must be a Solidity (.sol) file")

        if not os.path.exists(contract_path):
            raise FileNotFoundError(f"Contract not found: {contract_path}")

        print("\n========================================")
        print("HySCAV - Hybrid Smart Contract Analyzer")
        print("========================================")

        print(f"[PIPELINE] Contract: {contract_path}")

        all_issues: List[Dict[str, Any]] = []
        tool_outputs: Dict[str, Any] = {}

        # -------------------------------
        # 1. Slither Static Analysis
        # -------------------------------
        print("[SLITHER] Running static analysis...")

        slither_data: Optional[Dict[str, Any]] = run_slither(contract_path)

        if slither_data is None:
            print("[SLITHER][ERROR] Failed to run Slither")
            slither_data = {}

        slither_issues = simplify_slither_issues(slither_data)
        all_issues.extend(slither_issues)
        tool_outputs["Slither"] = {
            "issues_found": len(slither_issues),
            "raw_data": slither_data,
            "details": slither_issues
        }

        print(f"[SLITHER] Issues found: {len(slither_issues)}")

        # -------------------------------
        # 2. Feature Extraction
        # -------------------------------
        features = extract_slither_features(slither_data)

        print(f"[PIPELINE] Static features extracted: {features}")

        # -------------------------------
        # 3. ML Risk Prediction
        # -------------------------------
        risk_level, risk_score = predict_risk(features)

        print(f"[ML] Risk Level: {risk_level} (score = {risk_score})")

        # -------------------------------
        # 4. Decision Engine
        # -------------------------------
        next_tools = decide_next_stage(risk_level)

        print(f"[DECISION] Next tools to run: {next_tools}")

        # -------------------------------
        # 5. Mythril Analysis
        # -------------------------------
        if "Mythril" in next_tools:

            print("[PIPELINE] Launching Mythril analysis")

            mythril_data = run_mythril(contract_path)

            if mythril_data:
                mythril_issues = simplify_mythril_issues(mythril_data)
                all_issues.extend(mythril_issues)
                tool_outputs["Mythril"] = {
                    "issues_found": len(mythril_issues),
                    "raw_data": mythril_data,
                    "details": mythril_issues
                }
                print(f"[MYTHRIL] Issues found: {len(mythril_issues)}")
            else:
                tool_outputs["Mythril"] = {
                    "issues_found": 0,
                    "raw_data": {},
                    "details": []
                }
                print("[MYTHRIL] No issues detected")

        # -------------------------------
        # 6. Echidna Fuzzing
        # -------------------------------
        if "Echidna" in next_tools:

            print("[PIPELINE] Launching Echidna fuzzing")

            echidna_data = run_echidna(contract_path)

            if echidna_data:
                contract_name = os.path.splitext(os.path.basename(contract_path))[0]
                echidna_issues = simplify_echidna_issues(echidna_data, contract_name)
                all_issues.extend(echidna_issues)
                tool_outputs["Echidna"] = {
                    "issues_found": len(echidna_issues),
                    "raw_data": echidna_data,
                    "details": echidna_issues
                }
                print(f"[ECHIDNA] Issues found: {len(echidna_issues)}")
            else:
                tool_outputs["Echidna"] = {
                    "issues_found": 0,
                    "raw_data": {},
                    "details": []
                }
                print("[ECHIDNA] No issues detected")

        # -------------------------------
        # 7. Merge Issues
        # -------------------------------
        final_issues = merge_issues(all_issues)

        print(f"[PIPELINE] Total issues detected: {len(final_issues)}")

        # -------------------------------
        # 8. Generate Report
        # -------------------------------
        report_path = generate_report(
            contract_path,
            features,
            risk_level,
            risk_score,
            next_tools,
            final_issues,
            tool_outputs
        )

        pass  # report generation already logged inside generate_report()

        print("[PIPELINE] Hybrid analysis completed\n")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


# -------------------------------
# CLI Interface
# -------------------------------
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage:")
        print("python3 main.py analyze <contract.sol>")
        sys.exit(1)

    command = sys.argv[1]
    contract = sys.argv[2]

    if command == "analyze":
        # Check tools first
        tools = check_tools()
        print("Tool Status:")
        print(f"  Slither: {'OK' if tools['slither'] else 'NOT FOUND'}")
        print(f"  Docker: {'OK' if tools['docker'] else 'NOT FOUND'}")
        print("")
        
        if not tools["slither"]:
            print("[ERROR] Slither not installed. Run: pip install slither-analyzer")
            sys.exit(1)
        
        success = main(contract)
        sys.exit(0 if success else 1)

    else:
        print("Unknown command")
        sys.exit(1)

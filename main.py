"""
HySCAV - Hybrid Smart Contract Vulnerability Analyzer
Hybrid pipeline: Slither → ML Risk Model → Mythril → Echidna → Report
"""

import logging
import sys
import os
from typing import List, Dict, Any, Optional

from analyzers.slither_runner import run_slither, simplify_slither_issues
from analyzers.mythril_runner_docker import run_mythril, simplify_mythril_issues
from analyzers.echidna_runner_docker import run_echidna, simplify_echidna_issues

from controller.feature_extractor import extract_slither_features
from controller.decision_engine import decide_next_stage
from controller.merger import merge_issues

from ml.risk_model import predict_risk
from reports.report_generator import generate_report


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("HySCAV")


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

                print(f"[MYTHRIL] Issues found: {len(mythril_issues)}")
            else:
                print("[MYTHRIL] No issues detected")

        # -------------------------------
        # 6. Echidna Fuzzing
        # -------------------------------
        if "Echidna" in next_tools:

            print("[PIPELINE] Launching Echidna fuzzing")

            echidna_data = run_echidna(contract_path)

            if echidna_data:
                echidna_issues = simplify_echidna_issues(echidna_data)
                all_issues.extend(echidna_issues)

                print(f"[ECHIDNA] Issues found: {len(echidna_issues)}")
            else:
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
            final_issues
        )

        print(f"[REPORT] Report generated: {report_path}")

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
        success = main(contract)
        sys.exit(0 if success else 1)

    else:
        print("Unknown command")
        sys.exit(1)
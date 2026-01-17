import sys

from reports.report_generator import generate_report
from analyzers.slither_runner import run_slither, simplify_slither_issues
from analyzers.mythril_runner import run_mythril, simplify_mythril_issues
from analyzers.echidna_runner import run_echidna, simplify_echidna_issues

from controller.feature_extractor import extract_slither_features
from controller.decision_engine import decide_next_stage
from controller.merger import merge_issues
from ml.risk_model import predict_risk


def banner():
    print("=" * 45)
    print(" HySCAV - Hybrid Smart Contract Analyzer")
    print("=" * 45)


def analyze_contract(contract_path):
    print("[PIPELINE] Starting hybrid analysis pipeline")
    print(f"[PIPELINE] Contract: {contract_path}")

    all_issues = []

    # -------------------------------
    # 1. Static Analysis (Slither)
    # -------------------------------
    slither_data = run_slither(contract_path)
    slither_issues = simplify_slither_issues(slither_data)
    all_issues.extend(slither_issues)

    # -------------------------------
    # 2. Feature Extraction
    # -------------------------------
    features = extract_slither_features(slither_data)
    print(f"[PIPELINE] Static features extracted: {features}")

    # -------------------------------
    # 3. ML Risk Scoring
    # -------------------------------
    risk_level, risk_score = predict_risk(features)
    print(f"[ML] Risk Level: {risk_level} (score = {risk_score})")

    # -------------------------------
    # 4. Decision Engine
    # -------------------------------
    next_tools = decide_next_stage(risk_level)
    print(f"[DECISION] Next analysis tools: {next_tools}")

    # -------------------------------
    # 5. Symbolic Analysis (Mythril)
    # -------------------------------
    if "Mythril" in next_tools:
        print("[PIPELINE] Launching Mythril analysis")
        mythril_data = run_mythril(contract_path)
        mythril_issues = simplify_mythril_issues(mythril_data)

        all_issues.extend(mythril_issues)
        print(f"[MYTHRIL] Issues found: {len(mythril_issues)}")

    # -------------------------------
    # 6. Fuzzing Analysis (Echidna)  ✅ NEW
    # -------------------------------
    if "Echidna" in next_tools:
        print("[PIPELINE] Launching Echidna fuzzing")
        echidna_data = run_echidna(contract_path)
        echidna_issues = simplify_echidna_issues(echidna_data)

        all_issues.extend(echidna_issues)
        print(f"[ECHIDNA] Issues found: {len(echidna_issues)}")

    # -------------------------------
    # 7. Report Generation
    # -------------------------------
    final_issues = merge_issues(all_issues)

    generate_report(
        contract_path,
        features,
        risk_level,
        risk_score,
        next_tools,
        final_issues
    )

    print("[PIPELINE] Hybrid analysis completed")


def main():
    banner()

    if len(sys.argv) != 3 or sys.argv[1] != "analyze":
        print("Usage:")
        print("  python main.py analyze <contract_path>")
        sys.exit(1)

    contract_path = sys.argv[2]
    analyze_contract(contract_path)


if __name__ == "__main__":
    main()

import sys

from analyzers.slither_runner import run_slither
from controller.feature_extractor import extract_slither_features
from ml.risk_model import predict_risk
from controller.decision_engine import decide_next_stage


def banner():
    print("=" * 45)
    print(" HySCAV - Hybrid Smart Contract Analyzer")
    print("=" * 45)


def analyze_contract(contract_path):
    print("[PIPELINE] Starting hybrid analysis pipeline")
    print(f"[PIPELINE] Contract: {contract_path}")

    # -------------------------------
    # 1. Static Analysis (Slither)
    # -------------------------------
    slither_data = run_slither(contract_path)

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
    print(f"[DECISION] Next analysis tools to run: {next_tools}")

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

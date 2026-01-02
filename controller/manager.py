from analyzers.slither_runner import run_slither
from ml.feature_extractor import extract_slither_features


def run_pipeline(contract_path):
    print("[PIPELINE] Starting hybrid analysis pipeline")

    # Step 1: Static Analysis
    slither_output = run_slither(contract_path)

    # Step 2: Feature Extraction
    features = extract_slither_features(slither_output)
    print(f"[PIPELINE] Static features extracted: {features}")

    print("[PIPELINE] Slither stage completed")

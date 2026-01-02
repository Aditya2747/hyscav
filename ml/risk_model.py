import numpy as np

# Rule-based ML-style scorer (can be replaced by trained model)
def predict_risk(features):
    score = (
        features["high"] * 3 +
        features["medium"] * 2 +
        features["low"] * 1
    )

    if score >= 6:
        return "HIGH", score
    elif score >= 3:
        return "MEDIUM", score
    else:
        return "LOW", score


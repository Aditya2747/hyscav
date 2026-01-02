def extract_slither_features(slither_data):
    features = {
        "total_issues": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    if not slither_data:
        return features

    detectors = slither_data.get("results", {}).get("detectors", [])

    features["total_issues"] = len(detectors)

    for d in detectors:
        impact = d.get("impact", "").lower()
        if impact == "high":
            features["high"] += 1
        elif impact == "medium":
            features["medium"] += 1
        elif impact == "low":
            features["low"] += 1

    return features

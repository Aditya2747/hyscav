"""
Feature extraction module for HySCAV.

This module extracts numerical features from static analysis results
for use in ML-based risk scoring.
"""

from typing import Dict, Any, List


def extract_slither_features(slither_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract numerical features from Slither analysis results.

    Args:
        slither_data (Dict[str, Any]): Raw Slither analysis output

    Returns:
        Dict[str, int]: Dictionary containing:
            - total_issues: Total number of issues detected
            - high: Count of high severity issues
            - medium: Count of medium severity issues
            - low: Count of low severity issues

    Example:
        >>> data = {"results": {"detectors": [
        ...     {"impact": "high"}, {"impact": "medium"}, {"impact": "low"}
        ... ]}}
        >>> extract_slither_features(data)
        {'total_issues': 3, 'high': 1, 'medium': 1, 'low': 1}
    """
    features: Dict[str, int] = {
        "total_issues": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    if not slither_data:
        return features

    detectors = slither_data.get("results", {}).get("detectors", [])

    if not isinstance(detectors, list):
        return features

    features["total_issues"] = len(detectors)

    for d in detectors:
        if not isinstance(d, dict):
            continue
        impact = d.get("impact", "").lower()
        if impact == "high":
            features["high"] += 1
        elif impact == "medium":
            features["medium"] += 1
        elif impact == "low":
            features["low"] += 1

    return features


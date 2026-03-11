"""
Feature extraction module for HySCAV.

This module extracts numerical features from static analysis results
for use in ML-based risk scoring. It provides comprehensive feature
extraction including vulnerability counts, contract complexity metrics,
and specific vulnerability category detection.
"""

from typing import Dict, Any, List, Set, Optional
import logging

logger = logging.getLogger(__name__)

# High-risk vulnerability categories from SWC registry
HIGH_RISK_CATEGORIES: Set[str] = {
    "reentrancy",
    "arithmetic-overflow",
    "integer-overflow",
    "access-control",
    "unchecked-low-level-calls",
    "delegatecall",
    "front-running",
    "timestamp-dependence",
    "weak-randomness",
    "authorization-through-uid-overflow",
}

# Medium-risk vulnerability categories
MEDIUM_RISK_CATEGORIES: Set[str] = {
    "reentrancy-eth",
    "tx-origin",
    "dos",
    "denial-of-service",
    "ether-leakage",
    "unprotected-selfdestruct",
    "shadowing-state",
    "storage-packing",
    "missing-zero-check",
}

# Vulnerability check name mappings to categories
VULN_MAPPINGS: Dict[str, str] = {
    # High risk
    "reentrancy": "reentrancy",
    "reentrancy-no-eth-transfer": "reentrancy",
    "reentrancy-unlimited-gas": "reentrancy",
    "arithmetic": "arithmetic-overflow",
    "integer-overflow": "integer-overflow",
    "integer-underflow": "integer-overflow",
    "unchecked-low-level-call": "unchecked-low-level-calls",
    "unchecked-call-return-value": "unchecked-low-level-calls",
    "low-level-calls": "unchecked-low-level-calls",
    "delegatecall": "delegatecall",
    "delegatecall-to-user": "delegatecall",
    "external-function": "access-control",
    "public-function-that-could-be-external": "access-control",
    "tx-origin": "tx-origin",
    "tx-origin-usage": "tx-origin",
    "timestamp": "timestamp-dependence",
    "block-timestamp": "timestamp-dependence",
    "block-number": "timestamp-dependence",
    "weak-randomness": "weak-randomness",
    "weak-randomness-magic-value": "weak-randomness",
    # Medium risk
    "controlled-delegatecall": "delegatecall",
    "unused-return": "unchecked-low-level-calls",
    "boolean-constant": "access-control",
    "constant": "access-control",
    "immutable": "ether-leakage",
    "tax-transfer-frontend-running": "front-running",
    "division-before-multiplication": "arithmetic-overflow",
    "incorrect-equality": "access-control",
    "shadowing-abstract": "shadowing-state",
    "shadowing-local": "shadowing-state",
    "shadowing-state": "shadowing-state",
    "storage-packing": "storage-packing",
    "variable-scope": "shadowing-state",
    "uninitialized-local": "access-control",
    "uninitialized-storage": "access-control",
    "uninitialized-state": "access-control",
    "missing-calls": "dos",
    "too-many-digits": "integer-overflow",
}


def extract_slither_features(slither_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract comprehensive numerical features from Slither analysis results.

    This function extracts a rich set of features including:
    - Basic counts (total issues by severity)
    - Vulnerability category counts
    - Contract complexity metrics
    - Specific high-risk vulnerability flags

    Args:
        slither_data (Dict[str, Any]): Raw Slither analysis output

    Returns:
        Dict[str, Any]: Dictionary containing comprehensive features:
            - total_issues: Total number of issues detected
            - high: Count of high severity issues
            - medium: Count of medium severity issues
            - low: Count of low severity issues
            - high_risk_categories: Count of high-risk category issues
            - medium_risk_categories: Count of medium-risk category issues
            - unique_vuln_types: Number of unique vulnerability types
            - has_reentrancy: Boolean flag for reentrancy vulnerability
            - has_overflow: Boolean flag for overflow vulnerabilities
            - has_unchecked_call: Boolean flag for unchecked calls
            - has_access_control: Boolean flag for access control issues
            - contract_complexity: Estimated contract complexity score

    Example:
        >>> data = {"results": {"detectors": [
        ...     {"impact": "high", "check": "reentrancy"},
        ...     {"impact": "medium", "check": "tx-origin"}
        ... ]}}
        >>> features = extract_slither_features(data)
        >>> print(features["has_reentrancy"])
        True
    """
    features: Dict[str, Any] = {
        # Basic severity counts
        "total_issues": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        # Category counts
        "high_risk_categories": 0,
        "medium_risk_categories": 0,
        "unique_vuln_types": 0,
        # Specific vulnerability flags
        "has_reentrancy": False,
        "has_overflow": False,
        "has_unchecked_call": False,
        "has_access_control": False,
        "has_tx_origin": False,
        "has_delegatecall": False,
        "has_timestamp": False,
        "has_weak_randomness": False,
        # Complexity metrics
        "contract_complexity": 0,
        "external_calls": 0,
        "state_variables": 0,
    }

    if not slither_data:
        return features

    detectors = slither_data.get("results", {}).get("detectors", [])

    if not isinstance(detectors, list):
        logger.warning("Invalid detectors format in Slither data")
        return features

    features["total_issues"] = len(detectors)
    
    # Track unique vulnerability types
    vuln_types: Set[str] = set()
    
    # Track specific vulnerability check names
    check_names: List[str] = []

    for d in detectors:
        if not isinstance(d, dict):
            continue
        
        # Extract severity
        impact = d.get("impact", "").lower()
        if impact == "high":
            features["high"] += 1
        elif impact == "medium":
            features["medium"] += 1
        elif impact == "low":
            features["low"] += 1
        
        # Extract vulnerability check name
        check = d.get("check", "").lower()
        if check:
            vuln_types.add(check)
            check_names.append(check)
            
            # Map to category and set flags
            category = VULN_MAPPINGS.get(check, "")
            
            if category in HIGH_RISK_CATEGORIES:
                features["high_risk_categories"] += 1
            elif category in MEDIUM_RISK_CATEGORIES:
                features["medium_risk_categories"] += 1
            
            # Set specific vulnerability flags
            if "reentrancy" in category:
                features["has_reentrancy"] = True
            if "overflow" in category or "arithmetic" in category:
                features["has_overflow"] = True
            if "unchecked" in category or "low-level-call" in category:
                features["has_unchecked_call"] = True
            if "access-control" in category:
                features["has_access_control"] = True
            if "tx-origin" in category:
                features["has_tx_origin"] = True
            if "delegatecall" in category:
                features["has_delegatecall"] = True
            if "timestamp" in category:
                features["has_timestamp"] = True
            if "weak-randomness" in category:
                features["has_weak_randomness"] = True

    features["unique_vuln_types"] = len(vuln_types)
    
    # Extract contract information if available
    if "analysis" in slither_data:
        analysis = slither_data["analysis"]
        if isinstance(analysis, dict):
            # Count external calls
            if "external_calls" in analysis:
                features["external_calls"] = len(analysis["external_calls"])
            # Count state variables
            if "state_variables" in analysis:
                features["state_variables"] = len(analysis["state_variables"])
    
    # Calculate contract complexity based on number of issues and types
    features["contract_complexity"] = min(
        features["total_issues"] + 
        features["unique_vuln_types"] * 2 + 
        features["high_risk_categories"] * 3,
        100  # Cap at 100
    )

    logger.info(f"Extracted {features['total_issues']} issues with {features['unique_vuln_types']} unique types")
    logger.debug(f"Features: {features}")
    
    return features


def extract_contract_metrics(contract_info: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract contract-level complexity metrics.

    Args:
        contract_info (Dict[str, Any]): Contract information from Slither

    Returns:
        Dict[str, int]: Contract metrics including function count, etc.
    """
    metrics: Dict[str, int] = {
        "function_count": 0,
        "modifier_count": 0,
        "state_variable_count": 0,
        "event_count": 0,
    }

    if not contract_info:
        return metrics

    # These would be populated from Slither's contract analysis
    # For now, return default values
    return metrics


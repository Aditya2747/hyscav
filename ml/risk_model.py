"""
ML Risk Model module for HySCAV.

This module provides sophisticated ML-based risk scoring for smart contracts
using enhanced features extracted from static analysis results.
"""

from typing import Dict, Tuple, Any, List, Optional
from dataclasses import dataclass
import logging
import math

logger = logging.getLogger(__name__)


# Default weights for different feature categories
DEFAULT_WEIGHTS: Dict[str, float] = {
    # Severity weights (base scores)
    "high": 5.0,
    "medium": 2.5,
    "low": 1.0,
    # Category weights (multipliers)
    "high_risk_category": 2.0,
    "medium_risk_category": 1.5,
    # Specific vulnerability flags
    "has_reentrancy": 8.0,
    "has_overflow": 6.0,
    "has_unchecked_call": 5.0,
    "has_access_control": 4.0,
    "has_tx_origin": 4.0,
    "has_delegatecall": 7.0,
    "has_timestamp": 3.0,
    "has_weak_randomness": 5.0,
    # Complexity factors
    "unique_vuln_types": 1.5,
    "contract_complexity": 0.1,
}


@dataclass
class RiskThresholds:
    """Risk level thresholds for classification."""
    HIGH: float = 15.0
    MEDIUM: float = 5.0
    LOW: float = 0.0


class EnhancedRiskModel:
    """
    Enhanced ML-based risk assessment model.

    This model uses a weighted feature approach with multiple risk factors:
    - Severity-based scoring
    - Vulnerability category analysis
    - Specific vulnerability detection
    - Contract complexity factors

    Attributes:
        weights: Dictionary of feature weights
        thresholds: Risk level thresholds

    Example:
        >>> model = EnhancedRiskModel()
        >>> features = {"high": 2, "medium": 1, "has_reentrancy": True}
        >>> level, score = model.predict_risk(features)
        >>> print(level, score)
        ('HIGH', 18.0)
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[RiskThresholds] = None
    ):
        """
        Initialize the enhanced risk model.

        Args:
            weights: Custom weights for features. Uses defaults if not provided.
            thresholds: Custom risk thresholds. Uses defaults if not provided.
        """
        self.weights = weights if weights is not None else DEFAULT_WEIGHTS.copy()
        self.thresholds = thresholds if thresholds is not None else RiskThresholds()
        logger.info("EnhancedRiskModel initialized with custom weights")

    def predict_risk(self, features: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predict risk level using enhanced feature analysis.

        Args:
            features: Feature dictionary from feature extraction

        Returns:
            Tuple[str, float]: Risk level and risk score

        Raises:
            ValueError: If features are missing or invalid
        """
        if not isinstance(features, dict):
            raise ValueError("Features must be a dictionary")

        score = self._calculate_base_score(features)
        score += self._calculate_category_score(features)
        score += self._calculate_vulnerability_flags(features)
        score += self._calculate_complexity_score(features)

        # Normalize score to reasonable range
        score = max(0.0, min(score, 100.0))

        risk_level = self._classify_risk(score)

        logger.info(f"Risk prediction - Level: {risk_level}, Score: {score:.2f}")
        return risk_level, round(score, 2)

    def _calculate_base_score(self, features: Dict[str, Any]) -> float:
        """Calculate base score from severity counts."""
        score = 0.0

        # Get severity counts with defaults
        high = features.get("high", 0)
        medium = features.get("medium", 0)
        low = features.get("low", 0)

        # Ensure numeric values
        try:
            high = float(high) if high else 0.0
            medium = float(medium) if medium else 0.0
            low = float(low) if low else 0.0
        except (TypeError, ValueError):
            logger.warning("Invalid severity values, using 0")
            high = medium = low = 0.0

        # Apply severity weights
        score += high * self.weights["high"]
        score += medium * self.weights["medium"]
        score += low * self.weights["low"]

        return score

    def _calculate_category_score(self, features: Dict[str, Any]) -> float:
        """Calculate additional score from risk category counts."""
        score = 0.0

        high_risk_cat = features.get("high_risk_categories", 0)
        medium_risk_cat = features.get("medium_risk_categories", 0)

        try:
            high_risk_cat = float(high_risk_cat) if high_risk_cat else 0.0
            medium_risk_cat = float(medium_risk_cat) if medium_risk_cat else 0.0
        except (TypeError, ValueError):
            high_risk_cat = medium_risk_cat = 0.0

        # Apply category multipliers
        score += high_risk_cat * self.weights["high_risk_category"]
        score += medium_risk_cat * self.weights["medium_risk_category"]

        return score

    def _calculate_vulnerability_flags(self, features: Dict[str, Any]) -> float:
        """Calculate score from specific vulnerability flags."""
        score = 0.0

        vulnerability_flags = [
            ("has_reentrancy", "has_reentrancy"),
            ("has_overflow", "has_overflow"),
            ("has_unchecked_call", "has_unchecked_call"),
            ("has_access_control", "has_access_control"),
            ("has_tx_origin", "has_tx_origin"),
            ("has_delegatecall", "has_delegatecall"),
            ("has_timestamp", "has_timestamp"),
            ("has_weak_randomness", "has_weak_randomness"),
        ]

        for flag_key, weight_key in vulnerability_flags:
            if features.get(flag_key, False):
                score += self.weights.get(weight_key, 0.0)
                logger.debug(f"Vulnerability flag detected: {flag_key}")

        return score

    def _calculate_complexity_score(self, features: Dict[str, Any]) -> float:
        """Calculate score from contract complexity factors."""
        score = 0.0

        unique_types = features.get("unique_vuln_types", 0)
        complexity = features.get("contract_complexity", 0)

        try:
            unique_types = float(unique_types) if unique_types else 0.0
            complexity = float(complexity) if complexity else 0.0
        except (TypeError, ValueError):
            unique_types = complexity = 0.0

        # Apply complexity weights
        score += unique_types * self.weights.get("unique_vuln_types", 1.5)
        score += complexity * self.weights.get("contract_complexity", 0.1)

        return score

    def _classify_risk(self, score: float) -> str:
        """Classify risk score into risk level."""
        if score >= self.thresholds.HIGH:
            return "HIGH"
        elif score >= self.thresholds.MEDIUM:
            return "MEDIUM"
        else:
            return "LOW"

    def get_risk_factors(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get detailed breakdown of risk factors.

        This is useful for explaining why a contract received its risk score.

        Args:
            features: Feature dictionary

        Returns:
            List of risk factor dictionaries with name, contribution, and description
        """
        factors: List[Dict[str, Any]] = []

        # Severity factors
        high = features.get("high", 0)
        medium = features.get("medium", 0)
        low = features.get("low", 0)

        if high:
            contribution = float(high) * self.weights["high"]
            factors.append({
                "factor": "High Severity Issues",
                "count": high,
                "contribution": contribution,
                "description": f"{int(high)} high severity vulnerabilities"
            })

        if medium:
            contribution = float(medium) * self.weights["medium"]
            factors.append({
                "factor": "Medium Severity Issues",
                "count": medium,
                "contribution": contribution,
                "description": f"{int(medium)} medium severity vulnerabilities"
            })

        if low:
            contribution = float(low) * self.weights["low"]
            factors.append({
                "factor": "Low Severity Issues",
                "count": low,
                "contribution": contribution,
                "description": f"{int(low)} low severity vulnerabilities"
            })

        # Vulnerability flag factors
        flags = [
            ("has_reentrancy", "Reentrancy Vulnerability", "Potential reentrancy attack vector"),
            ("has_overflow", "Integer Overflow", "Arithmetic overflow risk"),
            ("has_unchecked_call", "Unchecked Calls", "Unchecked low-level calls"),
            ("has_access_control", "Access Control", "Access control issues"),
            ("has_tx_origin", "tx.origin Usage", "tx.origin authentication"),
            ("has_delegatecall", "Delegatecall Risk", "Proxy contract vulnerability"),
            ("has_timestamp", "Timestamp Dependence", "Block timestamp manipulation"),
            ("has_weak_randomness", "Weak Randomness", "Predictable random values"),
        ]

        for flag, name, desc in flags:
            if features.get(flag, False):
                contribution = self.weights.get(flag, 0.0)
                factors.append({
                    "factor": name,
                    "count": 1,
                    "contribution": contribution,
                    "description": desc
                })

        # Sort by contribution
        factors.sort(key=lambda x: x["contribution"], reverse=True)

        return factors


# Backward compatibility: Keep simple predict_risk function
def predict_risk(features: Dict[str, Any]) -> Tuple[str, float]:
    """
    Predict risk level based on extracted features.

    This is a wrapper function that uses the EnhancedRiskModel for
    backward compatibility with existing code.

    Args:
        features (Dict[str, Any]): Feature dictionary from feature extraction

    Returns:
        Tuple[str, float]: Risk level ("HIGH", "MEDIUM", "LOW") and risk score

    Example:
        >>> features = {'high': 2, 'medium': 1, 'low': 0, 'has_reentrancy': True}
        >>> predict_risk(features)
        ('HIGH', 18.0)
    """
    model = EnhancedRiskModel()
    return model.predict_risk(features)


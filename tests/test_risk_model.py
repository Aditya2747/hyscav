"""
Test suite for ML Risk Model.

This module tests the enhanced risk model with various vulnerability
combinations to ensure accurate risk scoring across all vulnerability types.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.risk_model import EnhancedRiskModel, predict_risk, DEFAULT_WEIGHTS
from controller.feature_extractor import extract_slither_features, HIGH_RISK_CATEGORIES


class TestRiskModelBasics(unittest.TestCase):
    """Test basic functionality of the risk model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = EnhancedRiskModel()

    def test_empty_features(self):
        """Test with empty features."""
        features = {}
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "LOW")
        self.assertEqual(score, 0.0)

    def test_zero_severity(self):
        """Test with zero severity counts."""
        features = {"high": 0, "medium": 0, "low": 0}
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "LOW")
        self.assertEqual(score, 0.0)

    def test_invalid_features(self):
        """Test with invalid features."""
        with self.assertRaises(ValueError):
            self.model.predict_risk("not a dict")


class TestSeverityScoring(unittest.TestCase):
    """Test severity-based scoring."""

    def setUp(self):
        self.model = EnhancedRiskModel()

    def test_single_high(self):
        """Test single high severity issue."""
        features = {"high": 1, "medium": 0, "low": 0}
        level, score = self.model.predict_risk(features)
        self.assertEqual(score, DEFAULT_WEIGHTS["high"])

    def test_single_medium(self):
        """Test single medium severity issue."""
        features = {"high": 0, "medium": 1, "low": 0}
        level, score = self.model.predict_risk(features)
        self.assertEqual(score, DEFAULT_WEIGHTS["medium"])

    def test_single_low(self):
        """Test single low severity issue."""
        features = {"high": 0, "medium": 0, "low": 1}
        level, score = self.model.predict_risk(features)
        self.assertEqual(score, DEFAULT_WEIGHTS["low"])

    def test_multiple_severities(self):
        """Test multiple severity levels combined."""
        features = {"high": 2, "medium": 2, "low": 2}
        level, score = self.model.predict_risk(features)
        expected = (2 * DEFAULT_WEIGHTS["high"] + 
                   2 * DEFAULT_WEIGHTS["medium"] + 
                   2 * DEFAULT_WEIGHTS["low"])
        self.assertEqual(score, expected)

    def test_high_risk_classification(self):
        """Test HIGH risk classification."""
        features = {"high": 3, "medium": 1, "low": 1}
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "HIGH")

    def test_medium_risk_classification(self):
        """Test MEDIUM risk classification."""
        features = {"high": 1, "medium": 1, "low": 0}
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "MEDIUM")


class TestVulnerabilityFlags(unittest.TestCase):
    """Test specific vulnerability flag detection."""

    def setUp(self):
        self.model = EnhancedRiskModel()

    def test_reentrancy_flag(self):
        """Test reentrancy vulnerability flag."""
        features = {"high": 0, "medium": 0, "low": 0, "has_reentrancy": True}
        level, score = self.model.predict_risk(features)
        self.assertGreater(score, 0)
        self.assertEqual(level, "HIGH")

    def test_overflow_flag(self):
        """Test overflow vulnerability flag."""
        features = {"high": 0, "medium": 0, "low": 0, "has_overflow": True}
        level, score = self.model.predict_risk(features)
        self.assertGreater(score, 0)

    def test_unchecked_call_flag(self):
        """Test unchecked call vulnerability flag."""
        features = {"high": 0, "medium": 0, "low": 0, "has_unchecked_call": True}
        level, score = self.model.predict_risk(features)
        self.assertGreater(score, 0)

    def test_delegatecall_flag(self):
        """Test delegatecall vulnerability flag."""
        features = {"high": 0, "medium": 0, "low": 0, "has_delegatecall": True}
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "HIGH")

    def test_multiple_flags(self):
        """Test multiple vulnerability flags combined."""
        features = {
            "high": 0, "medium": 0, "low": 0,
            "has_reentrancy": True,
            "has_overflow": True,
            "has_unchecked_call": True
        }
        level, score = self.model.predict_risk(features)
        # Should have significant score from multiple flags
        self.assertGreaterEqual(score, 15.0)
        self.assertEqual(level, "HIGH")


class TestCategoryScoring(unittest.TestCase):
    """Test vulnerability category scoring."""

    def setUp(self):
        self.model = EnhancedRiskModel()

    def test_high_risk_categories(self):
        """Test high risk category count."""
        features = {
            "high": 0, "medium": 0, "low": 0,
            "high_risk_categories": 3,
            "medium_risk_categories": 0
        }
        level, score = self.model.predict_risk(features)
        expected = 3 * DEFAULT_WEIGHTS["high_risk_category"]
        self.assertEqual(score, expected)

    def test_medium_risk_categories(self):
        """Test medium risk category count."""
        features = {
            "high": 0, "medium": 0, "low": 0,
            "high_risk_categories": 0,
            "medium_risk_categories": 2
        }
        level, score = self.model.predict_risk(features)
        expected = 2 * DEFAULT_WEIGHTS["medium_risk_category"]
        self.assertEqual(score, expected)


class TestComplexityFactors(unittest.TestCase):
    """Test contract complexity scoring."""

    def setUp(self):
        self.model = EnhancedRiskModel()

    def test_unique_vuln_types(self):
        """Test unique vulnerability types scoring."""
        features = {
            "high": 0, "medium": 0, "low": 0,
            "unique_vuln_types": 5,
            "contract_complexity": 0
        }
        level, score = self.model.predict_risk(features)
        expected = 5 * DEFAULT_WEIGHTS["unique_vuln_types"]
        self.assertEqual(score, expected)

    def test_contract_complexity(self):
        """Test contract complexity scoring."""
        features = {
            "high": 0, "medium": 0, "low": 0,
            "unique_vuln_types": 0,
            "contract_complexity": 50
        }
        level, score = self.model.predict_risk(features)
        expected = 50 * DEFAULT_WEIGHTS["contract_complexity"]
        self.assertEqual(score, expected)


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world vulnerability scenarios."""

    def setUp(self):
        self.model = EnhancedRiskModel()

    def test_reentrancy_attack(self):
        """Test typical reentrancy attack scenario."""
        features = {
            "high": 2,
            "medium": 1,
            "low": 0,
            "high_risk_categories": 1,
            "medium_risk_categories": 0,
            "has_reentrancy": True,
            "has_unchecked_call": True,
            "unique_vuln_types": 3,
            "contract_complexity": 15
        }
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "HIGH")
        self.assertGreater(score, 20.0)

    def test_integer_overflow(self):
        """Test integer overflow vulnerability."""
        features = {
            "high": 1,
            "medium": 2,
            "low": 1,
            "high_risk_categories": 1,
            "medium_risk_categories": 0,
            "has_overflow": True,
            "has_unchecked_call": False,
            "unique_vuln_types": 2,
            "contract_complexity": 10
        }
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "HIGH")

    def test_access_control_issue(self):
        """Test access control vulnerability."""
        features = {
            "high": 1,
            "medium": 0,
            "low": 2,
            "high_risk_categories": 0,
            "medium_risk_categories": 1,
            "has_access_control": True,
            "has_tx_origin": True,
            "unique_vuln_types": 2,
            "contract_complexity": 8
        }
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "HIGH")

    def test_clean_contract(self):
        """Test clean contract with no vulnerabilities."""
        features = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "high_risk_categories": 0,
            "medium_risk_categories": 0,
            "has_reentrancy": False,
            "has_overflow": False,
            "has_unchecked_call": False,
            "has_access_control": False,
            "unique_vuln_types": 0,
            "contract_complexity": 0
        }
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "LOW")
        self.assertEqual(score, 0.0)

    def test_only_low_severity(self):
        """Test contract with only low severity issues."""
        features = {
            "high": 0,
            "medium": 0,
            "low": 3,
            "high_risk_categories": 0,
            "medium_risk_categories": 0,
            "unique_vuln_types": 3,
            "contract_complexity": 5
        }
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "LOW")

    def test_medium_risk_boundary(self):
        """Test boundary case for medium risk."""
        features = {
            "high": 1,
            "medium": 0,
            "low": 0,
            "high_risk_categories": 0,
            "medium_risk_categories": 0,
            "unique_vuln_types": 1,
            "contract_complexity": 0
        }
        level, score = self.model.predict_risk(features)
        self.assertEqual(level, "MEDIUM")


class TestFeatureExtractor(unittest.TestCase):
    """Test feature extraction from Slither data."""

    def test_empty_data(self):
        """Test with empty Slither data."""
        features = extract_slither_features({})
        self.assertEqual(features["total_issues"], 0)
        self.assertEqual(features["high"], 0)

    def test_single_issue(self):
        """Test with single issue."""
        slither_data = {
            "results": {
                "detectors": [
                    {"impact": "high", "check": "reentrancy"}
                ]
            }
        }
        features = extract_slither_features(slither_data)
        self.assertEqual(features["total_issues"], 1)
        self.assertEqual(features["high"], 1)
        self.assertTrue(features["has_reentrancy"])

    def test_multiple_issues(self):
        """Test with multiple issues."""
        slither_data = {
            "results": {
                "detectors": [
                    {"impact": "high", "check": "reentrancy"},
                    {"impact": "medium", "check": "tx-origin"},
                    {"impact": "low", "check": "unused-return"}
                ]
            }
        }
        features = extract_slither_features(slither_data)
        self.assertEqual(features["total_issues"], 3)
        self.assertEqual(features["high"], 1)
        self.assertEqual(features["medium"], 1)
        self.assertEqual(features["low"], 1)
        self.assertTrue(features["has_reentrancy"])
        self.assertTrue(features["has_tx_origin"])

    def test_overflow_detection(self):
        """Test overflow vulnerability detection."""
        slither_data = {
            "results": {
                "detectors": [
                    {"impact": "high", "check": "integer-overflow"},
                    {"impact": "high", "check": "integer-underflow"}
                ]
            }
        }
        features = extract_slither_features(slither_data)
        self.assertTrue(features["has_overflow"])

    def test_unchecked_call_detection(self):
        """Test unchecked call detection."""
        slither_data = {
            "results": {
                "detectors": [
                    {"impact": "high", "check": "unchecked-low-level-call"}
                ]
            }
        }
        features = extract_slither_features(slither_data)
        self.assertTrue(features["has_unchecked_call"])

    def test_unique_vuln_types(self):
        """Test unique vulnerability type counting."""
        slither_data = {
            "results": {
                "detectors": [
                    {"impact": "high", "check": "reentrancy"},
                    {"impact": "high", "check": "reentrancy"},
                    {"impact": "medium", "check": "tx-origin"}
                ]
            }
        }
        features = extract_slither_features(slither_data)
        self.assertEqual(features["unique_vuln_types"], 2)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with predict_risk function."""

    def test_simple_features(self):
        """Test with simple feature dict."""
        features = {"high": 2, "medium": 1, "low": 0}
        level, score = predict_risk(features)
        self.assertEqual(level, "HIGH")
        self.assertGreater(score, 0)

    def test_extended_features(self):
        """Test with extended feature dict."""
        features = {
            "high": 1,
            "medium": 1,
            "low": 1,
            "has_reentrancy": True,
            "has_overflow": False
        }
        level, score = predict_risk(features)
        self.assertEqual(level, "HIGH")


class TestRiskFactors(unittest.TestCase):
    """Test risk factor breakdown functionality."""

    def setUp(self):
        self.model = EnhancedRiskModel()

    def test_risk_factors_output(self):
        """Test get_risk_factors returns correct structure."""
        features = {
            "high": 2,
            "medium": 1,
            "low": 0,
            "has_reentrancy": True
        }
        factors = self.model.get_risk_factors(features)
        self.assertIsInstance(factors, list)
        self.assertGreater(len(factors), 0)

    def test_risk_factors_sorted(self):
        """Test risk factors are sorted by contribution."""
        features = {
            "high": 1,
            "medium": 1,
            "low": 1,
            "has_reentrancy": True
        }
        factors = self.model.get_risk_factors(features)
        contributions = [f["contribution"] for f in factors]
        self.assertEqual(contributions, sorted(contributions, reverse=True))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)


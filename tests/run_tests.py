"""
Test runner for HySCAV ML Risk Model.

This script runs comprehensive tests on the risk model using sample
vulnerable contracts to ensure accurate vulnerability detection.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.risk_model import EnhancedRiskModel, predict_risk
from controller.feature_extractor import extract_slither_features
from tests.test_contracts import TEST_SCENARIOS, get_test_data


def print_header(title: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_result(name: str, level: str, score: float, expected_level: str, 
                 expected_min: float, passed: bool) -> None:
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status}: {name}")
    print(f"  Risk Level: {level} (expected: {expected_level})")
    print(f"  Risk Score: {score:.2f} (min expected: {expected_min:.2f})")


def run_scenario_tests() -> None:
    """Run tests for all vulnerability scenarios."""
    print_header("Running Scenario Tests")
    
    model = EnhancedRiskModel()
    passed = 0
    failed = 0
    
    for scenario in TEST_SCENARIOS:
        # Get sample data
        slither_data = get_test_data(scenario["data_name"])
        
        # Extract features
        features = extract_slither_features(slither_data)
        
        # Get risk prediction
        risk_level, risk_score = model.predict_risk(features)
        
        # Check if test passed
        test_passed = (
            risk_level == scenario["expected_level"] and
            risk_score >= scenario["expected_min_score"]
        )
        
        if test_passed:
            passed += 1
        else:
            failed += 1
        
        print_result(
            scenario["name"],
            risk_level,
            risk_score,
            scenario["expected_level"],
            scenario["expected_min_score"],
            test_passed
        )
        
        # Print key features
        print(f"  Key Features:")
        print(f"    - Total Issues: {features.get('total_issues', 0)}")
        print(f"    - High: {features.get('high', 0)}, Medium: {features.get('medium', 0)}, Low: {features.get('low', 0)}")
        
        # Print vulnerability flags
        flags = []
        for flag in ['has_reentrancy', 'has_overflow', 'has_unchecked_call', 
                     'has_access_control', 'has_tx_origin', 'has_delegatecall',
                     'has_timestamp', 'has_weak_randomness']:
            if features.get(flag, False):
                flags.append(flag.replace('has_', ''))
        if flags:
            print(f"    - Vulnerabilities: {', '.join(flags)}")
    
    # Print summary
    print_header("Test Summary")
    total = passed + failed
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    return failed == 0


def run_unit_tests() -> None:
    """Run unit tests using unittest."""
    print_header("Running Unit Tests")
    
    import unittest
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def test_feature_extraction() -> None:
    """Test feature extraction from Slither data."""
    print_header("Testing Feature Extraction")
    
    model = EnhancedRiskModel()
    
    # Test various vulnerability types
    test_cases = [
        ("Reentrancy", "reentrancy"),
        ("Overflow", "overflow"),
        ("Unchecked Calls", "unchecked_calls"),
        ("tx.origin", "tx_origin"),
        ("Delegatecall", "delegatecall"),
        ("Timestamp", "timestamp"),
        ("Weak Randomness", "weak_randomness"),
    ]
    
    print("\nVulnerability Detection Results:")
    print("-" * 50)
    
    for name, data_name in test_cases:
        slither_data = get_test_data(data_name)
        features = extract_slither_features(slither_data)
        
        # Find which flags are set
        flags_detected = []
        for flag in features:
            if flag.startswith('has_') and features.get(flag, False):
                flags_detected.append(flag.replace('has_', ''))
        
        print(f"\n{name}:")
        print(f"  Issues: {features.get('total_issues', 0)}")
        print(f"  Flags Detected: {', '.join(flags_detected) if flags_detected else 'None'}")
        
        level, score = model.predict_risk(features)
        print(f"  Risk: {level} ({score:.2f})")


def test_backward_compatibility() -> None:
    """Test backward compatibility with predict_risk function."""
    print_header("Testing Backward Compatibility")
    
    test_cases = [
        ({"high": 0, "medium": 0, "low": 0}, "LOW", 0.0),
        ({"high": 1, "medium": 0, "low": 0}, "MEDIUM", 5.0),
        ({"high": 2, "medium": 1, "low": 0}, "MEDIUM", 10.0),
        ({"high": 3, "medium": 2, "low": 1}, "HIGH", 20.5),
    ]
    
    print("\nCompatibility Test Results:")
    print("-" * 50)
    
    all_passed = True
    for features, expected_level, expected_min_score in test_cases:
        level, score = predict_risk(features)
        
        passed = level == expected_level and score >= expected_min_score
        all_passed = all_passed and passed
        
        status = "✓" if passed else "✗"
        print(f"\n{status} Features: {features}")
        print(f"   Result: {level} ({score:.2f})")
        print(f"   Expected: {expected_level} (min {expected_min_score})")
    
    print(f"\n{'All tests passed!' if all_passed else 'Some tests failed!'}")


def main():
    """Main test runner."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                  HySCAV ML Risk Model Test Suite                     ║
║                                                                      ║
║  Testing vulnerability detection and risk scoring across all         ║
║  common smart contract vulnerability types.                          ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run all tests
    scenario_passed = run_scenario_tests()
    test_feature_extraction()
    test_backward_compatibility()
    
    print_header("All Tests Complete")
    print("""
You can also run the unit tests separately with:
    python -m pytest tests/ -v
or:
    python -m unittest discover tests/ -v
    """)
    
    return 0 if scenario_passed else 1


if __name__ == "__main__":
    sys.exit(main())


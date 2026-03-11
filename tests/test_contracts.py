"""
Test contracts with various vulnerability types for testing the ML risk model.

This module provides sample Solidity contracts with specific vulnerabilities
that can be used to test the analysis pipeline and risk scoring.
"""

# Sample Slither analysis results for different vulnerability types
# These mimic real Slither output for testing purposes

SAMPLE_SLITHER_DATA = {
    # Reentrancy vulnerability (HIGH)
    "reentrancy": {
        "results": {
            "detectors": [
                {
                    "check": "reentrancy",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Reentrancy vulnerability detected",
                    "elements": [
                        {
                            "type": "function",
                            "name": "withdraw",
                            "source_mapping": {"lines": [25, 26, 27]}
                        }
                    ]
                },
                {
                    "check": "reentrancy-no-eth-transfer",
                    "impact": "high",
                    "confidence": "medium",
                    "description": "Reentrancy possible",
                    "elements": []
                }
            ]
        }
    },
    
    # Integer Overflow (HIGH)
    "overflow": {
        "results": {
            "detectors": [
                {
                    "check": "integer-overflow",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Integer overflow possible",
                    "elements": []
                },
                {
                    "check": "integer-underflow",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Integer underflow possible",
                    "elements": []
                }
            ]
        }
    },
    
    # Access Control (HIGH)
    "access_control": {
        "results": {
            "detectors": [
                {
                    "check": "external-function",
                    "impact": "low",
                    "confidence": "high",
                    "description": "Public function could be external",
                    "elements": []
                },
                {
                    "check": "public-function-that-could-be-external",
                    "impact": "low",
                    "confidence": "high",
                    "description": "Function visibility can be restricted",
                    "elements": []
                }
            ]
        }
    },
    
    # Unchecked Low-Level Calls (HIGH)
    "unchecked_calls": {
        "results": {
            "detectors": [
                {
                    "check": "unchecked-low-level-call",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Return value of low-level call not checked",
                    "elements": []
                },
                {
                    "check": "unused-return",
                    "impact": "medium",
                    "confidence": "medium",
                    "description": "Return value not used",
                    "elements": []
                }
            ]
        }
    },
    
    # tx.origin usage (MEDIUM)
    "tx_origin": {
        "results": {
            "detectors": [
                {
                    "check": "tx-origin",
                    "impact": "medium",
                    "confidence": "high",
                    "description": "Use of tx.origin for authorization",
                    "elements": []
                }
            ]
        }
    },
    
    # Delegatecall vulnerability (HIGH)
    "delegatecall": {
        "results": {
            "detectors": [
                {
                    "check": "delegatecall",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Delegatecall usage detected",
                    "elements": []
                },
                {
                    "check": "controlled-delegatecall",
                    "impact": "high",
                    "confidence": "medium",
                    "description": "Delegatecall to user-controlled address",
                    "elements": []
                }
            ]
        }
    },
    
    # Timestamp dependence (MEDIUM)
    "timestamp": {
        "results": {
            "detectors": [
                {
                    "check": "timestamp",
                    "impact": "medium",
                    "confidence": "medium",
                    "description": "Block timestamp dependence detected",
                    "elements": []
                }
            ]
        }
    },
    
    # Weak Randomness (MEDIUM)
    "weak_randomness": {
        "results": {
            "detectors": [
                {
                    "check": "weak-randomness",
                    "impact": "medium",
                    "confidence": "high",
                    "description": "Weak randomness detected",
                    "elements": []
                }
            ]
        }
    },
    
    # Multiple vulnerabilities combined (CRITICAL)
    "critical": {
        "results": {
            "detectors": [
                {
                    "check": "reentrancy",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Reentrancy vulnerability"
                },
                {
                    "check": "integer-overflow",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Integer overflow"
                },
                {
                    "check": "unchecked-low-level-call",
                    "impact": "high",
                    "confidence": "high",
                    "description": "Unchecked call"
                },
                {
                    "check": "tx-origin",
                    "impact": "medium",
                    "confidence": "high",
                    "description": "tx.origin usage"
                },
                {
                    "check": "weak-randomness",
                    "impact": "medium",
                    "confidence": "high",
                    "description": "Weak randomness"
                }
            ]
        }
    },
    
    # Clean contract (LOW)
    "clean": {
        "results": {
            "detectors": []
        }
    },
    
    # Only low severity issues (no vulnerability flags)
    "low_only": {
        "results": {
            "detectors": [
                {
                    "check": "constant",
                    "impact": "low",
                    "confidence": "high",
                    "description": "State variable could be constant"
                },
                {
                    "check": "naming-convention",
                    "impact": "low",
                    "confidence": "high",
                    "description": "Naming convention violation"
                }
            ]
        }
    }
}


def get_test_data(name: str) -> dict:
    """
    Get sample Slither data for testing.
    
    Args:
        name: Name of the vulnerability type ('reentrancy', 'overflow', etc.)
        
    Returns:
        dict: Sample Slither analysis result
    """
    return SAMPLE_SLITHER_DATA.get(name, {})


# Test scenarios with expected results
TEST_SCENARIOS = [
    {
        "name": "Reentrancy Attack",
        "data_name": "reentrancy",
        "expected_level": "HIGH",
        "expected_min_score": 10.0,
        "description": "Classic reentrancy vulnerability"
    },
    {
        "name": "Integer Overflow",
        "data_name": "overflow",
        "expected_level": "HIGH", 
        "expected_min_score": 10.0,
        "description": "Arithmetic overflow vulnerabilities"
    },
    {
        "name": "Access Control Issues",
        "data_name": "access_control",
        "expected_level": "MEDIUM",
        "expected_min_score": 3.0,
        "description": "Access control and visibility issues"
    },
    {
        "name": "Unchecked Calls",
        "data_name": "unchecked_calls",
        "expected_level": "HIGH",
        "expected_min_score": 10.0,
        "description": "Unchecked low-level calls"
    },
    {
        "name": "tx.origin Usage",
        "data_name": "tx_origin",
        "expected_level": "MEDIUM",
        "expected_min_score": 3.0,
        "description": "tx.origin authentication vulnerability"
    },
    {
        "name": "Delegatecall Risk",
        "data_name": "delegatecall",
        "expected_level": "HIGH",
        "expected_min_score": 10.0,
        "description": "Dangerous delegatecall usage"
    },
    {
        "name": "Timestamp Dependence",
        "data_name": "timestamp",
        "expected_level": "MEDIUM",
        "expected_min_score": 3.0,
        "description": "Block timestamp manipulation risk"
    },
    {
        "name": "Weak Randomness",
        "data_name": "weak_randomness",
        "expected_level": "MEDIUM",
        "expected_min_score": 3.0,
        "description": "Predictable random values"
    },
    {
        "name": "Critical Multiple",
        "data_name": "critical",
        "expected_level": "HIGH",
        "expected_min_score": 25.0,
        "description": "Multiple critical vulnerabilities"
    },
    {
        "name": "Clean Contract",
        "data_name": "clean",
        "expected_level": "LOW",
        "expected_min_score": 0.0,
        "description": "No vulnerabilities detected"
    },
    {
        "name": "Low Severity Only",
        "data_name": "low_only",
        "expected_level": "MEDIUM",
        "expected_min_score": 3.0,
        "description": "Only low severity issues"
    }
]


if __name__ == "__main__":
    # Print test scenarios
    print("=" * 70)
    print("HySCAV Test Scenarios")
    print("=" * 70)
    
    for scenario in TEST_SCENARIOS:
        print(f"\n{scenario['name']}")
        print(f"  Description: {scenario['description']}")
        print(f"  Expected Level: {scenario['expected_level']}")
        print(f"  Min Score: {scenario['expected_min_score']}")


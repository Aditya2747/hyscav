"""
Report generator module for HySCAV.

This module generates JSON reports containing analysis results,
including vulnerability findings, risk assessments, and tool execution details.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def generate_report(
    contract_path: str,
    features: Dict[str, Any],
    risk_level: str,
    risk_score: float,
    tools_run: List[str],
    issues: List[Dict[str, Any]]
) -> str:
    """
    Generate a JSON report with analysis results.

    This function creates a comprehensive report containing:
    - Contract information
    - Static analysis features
    - Risk assessment results
    - Tools that were executed
    - Vulnerability details

    Args:
        contract_path (str): Path to the analyzed Solidity contract
        features (Dict[str, Any]): Feature dictionary from feature extraction
        risk_level (str): Risk level ("HIGH", "MEDIUM", "LOW")
        risk_score (float): Numeric risk score
        tools_run (List[str]): List of analysis tools that were executed
        issues (List[Dict[str, Any]]): List of vulnerability issues found

    Returns:
        str: Path to the generated report file

    Example:
        >>> report_path = generate_report(
        ...     "contracts/Bank.sol",
        ...     {"high": 1, "medium": 2, "low": 3},
        ...     "HIGH", 7.0,
        ...     ["Slither", "Mythril"],
        ...     [{"tool": "slither", "title": "reentrancy"}]
        ... )
        >>> print(report_path)
        reports/report_Bank.sol.json
    """
    report: Dict[str, Any] = {
        "contract": os.path.basename(contract_path),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "static_analysis_features": features,
        "risk_assessment": {
            "risk_level": risk_level,
            "risk_score": risk_score
        },
        "tools_executed": tools_run,
        "vulnerabilities": {
            "total": len(issues),
            "details": issues
        }
    }

    report_dir: str = "reports"
    os.makedirs(report_dir, exist_ok=True)

    report_file: str = os.path.join(
        report_dir,
        f"report_{os.path.basename(contract_path)}.json"
    )

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        logger.info(f"[REPORT] Report generated: {report_file}")
    except Exception as e:
        logger.error(f"[REPORT] Failed to generate report: {e}")
        raise

    return report_file


"""
Mythril runner module for HySCAV.

This module provides functions to run Mythril symbolic execution
analysis on Solidity smart contracts.
"""

import subprocess
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def run_mythril(contract_path: str) -> Dict[str, Any]:
    """
    Run Mythril symbolic execution analysis on a Solidity contract.

    Args:
        contract_path (str): Path to the Solidity contract file

    Returns:
        Dict[str, Any]: Dictionary containing issues found by Mythril.
            Returns {"issues": []} if no issues detected or analysis fails.

    Example:
        >>> result = run_mythril("contracts/Bank.sol")
        >>> print(result["issues"])
        [...]
    """
    logger.info("[MYTHRIL] Running symbolic execution...")

    command: List[str] = [
        "myth",
        "analyze",
        contract_path,
        "--execution-timeout",
        "60",
        "--output",
        "json"
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    if not result.stdout:
        logger.info("[MYTHRIL] No issues detected")
        return {"issues": []}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logger.error(f"[MYTHRIL][ERROR] Failed to parse output: {e}")
        return {"issues": []}

    issues = data.get("issues", [])
    logger.info(f"[MYTHRIL] Issues found: {len(issues)}")

    return {"issues": issues}


def simplify_mythril_issues(mythril_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert Mythril issues to HySCAV unified issue format.

    Args:
        mythril_result (Dict[str, Any]): Raw Mythril output containing issues

    Returns:
        List[Dict[str, Any]]: List of simplified issues with standardized keys:
            - tool: Always "mythril"
            - title: Issue title
            - severity: Issue severity
            - contract: Contract name
            - function: Function name
            - line: Line number
            - swc-id: SWC registry ID
            - description: Issue description

    Example:
        >>> result = {"issues": [{"title": "Integer Overflow", "severity": "High"}]}
        >>> simplify_mythril_issues(result)
        [{'tool': 'mythril', 'title': 'Integer Overflow', 'severity': 'High', ...}]
    """
    simplified: List[Dict[str, Any]] = []

    if not isinstance(mythril_result, dict):
        logger.warning("Invalid mythril_result format")
        return simplified

    for issue in mythril_result.get("issues", []):
        if not isinstance(issue, dict):
            continue

        simplified.append({
            "tool": "mythril",
            "title": issue.get("title"),
            "severity": issue.get("severity"),
            "contract": issue.get("contract"),
            "function": issue.get("function"),
            "line": issue.get("lineno"),
            "swc-id": issue.get("swc-id"),
            "description": issue.get("description")
        })

    logger.debug(f"Simplified {len(simplified)} Mythril issues")
    return simplified


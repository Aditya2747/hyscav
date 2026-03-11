"""
Echidna runner module for HySCAV.

This module provides functions to run Echidna fuzzing analysis
on Solidity smart contracts using Docker.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Docker image for Echidna
ECHIDNA_IMAGE: str = "ghcr.io/crytic/echidna/echidna:latest"


def run_echidna(contract_path: str, report_dir: str = "reports") -> Dict[str, Any]:
    """
    Run Echidna fuzzing analysis on a Solidity contract.

    This function runs Echidna inside a Docker container to perform
    property-based fuzzing on the smart contract.

    Args:
        contract_path (str): Path to the Solidity contract file
        report_dir (str): Directory to save Echidna report files

    Returns:
        Dict[stridna JSON, Any]: Ech output containing test results.
            Returns empty dict if analysis fails or no properties detected.

    Example:
        >>> result = run_echidna("contracts/Bank.sol")
        >>> print(result)
        {"test1": {"status": "passed"}, "test2": {"status": "failed"}}
    """
    contract_path = Path(contract_path).resolve()
    report_dir = Path(report_dir).resolve()
    report_dir.mkdir(exist_ok=True)

    output_file = report_dir / "echidna.json"

    # Ensure path is inside project root (for Docker mount)
    project_root = Path.cwd()
    relative_contract = contract_path.relative_to(project_root)

    cmd: List[str] = [
        "docker", "run", "--rm",
        "-v", f"{project_root}:/src",
        ECHIDNA_IMAGE,
        "echidna-test",
        f"/src/{relative_contract}",
        "--config", "/src/echidna.yaml",
        "--format", "json",
        "--output", "/src/reports/echidna.json"
    ]

    logger.info("[ECHIDNA] Running Echidna fuzzing...")

    # IMPORTANT: Echidna exits non-zero when it finds issues or no properties
    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except Exception as e:
        logger.error(f"[ECHIDNA] Failed to run Docker: {e}")
        return {}

    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("[ECHIDNA] Analysis completed successfully")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"[ECHIDNA] Failed to parse JSON output: {e}")
        except Exception as e:
            logger.error(f"[ECHIDNA] Error reading output: {e}")

    logger.info("[ECHIDNA] No findings or no properties detected")
    return {}


def simplify_echidna_issues(echidna_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert raw Echidna JSON into HySCAV unified issue format.

    Args:
        echidna_data (Dict[str, Any]): Raw Echidna JSON output from run_echidna

    Returns:
        List[Dict[str, Any]]: List of simplified issues with standardized keys:
            - tool: Always "Echidna"
            - type: Always "Property Violation"
            - description: Description of the failed property
            - severity: Always "High"
            - contract: Contract name

    Example:
        >>> data = {"test_balance": {"status": "failed", "contract": "Bank"}}
        >>> simplify_echidna_issues(data)
        [{'tool': 'Echidna', 'type': 'Property Violation', ...}]
    """
    issues: List[Dict[str, Any]] = []

    if not echidna_data or not isinstance(echidna_data, dict):
        logger.debug("No Echidna data to simplify")
        return issues

    for test_name, test_data in echidna_data.items():
        if not isinstance(test_data, dict):
            continue

        if test_data.get("status") == "failed":
            issues.append({
                "tool": "Echidna",
                "type": "Property Violation",
                "description": f"Echidna property failed: {test_name}",
                "severity": "High",
                "contract": test_data.get("contract", "Unknown"),
                "test_name": test_name
            })
            logger.debug(f"Found failed property: {test_name}")

    logger.info(f"Simplified {len(issues)} Echidna issues")
    return issues


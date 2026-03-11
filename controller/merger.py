"""
Issue merger module for HySCAV.

This module handles merging and deduplication of vulnerability issues
from multiple analysis tools (Slither, Mythril, Echidna).
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def merge_issues(all_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge and deduplicate issues from all analyzers.

    This function removes duplicate issues based on a composite key
    consisting of tool, type, description, and contract.

    Args:
        all_issues (List[Dict[str, Any]]): List of issues from all analyzers.
            Each issue should be a dictionary with keys like 'tool', 'type',
            'description', 'contract', etc.

    Returns:
        List[Dict[str, Any]]: Deduplicated list of issues

    Example:
        >>> issues = [
        ...     {"tool": "slither", "type": "reentrancy", "description": "...", "contract": "Bank"},
        ...     {"tool": "slither", "type": "reentrancy", "description": "...", "contract": "Bank"}
        ... ]
        >>> merged = merge_issues(issues)
        >>> len(merged)
        1
    """
    seen: set = set()
    merged: List[Dict[str, Any]] = []

    for issue in all_issues:
        if not isinstance(issue, dict):
            logger.warning(f"Skipping non-dict issue: {type(issue)}")
            continue

        key: Tuple[str, str, str, str] = (
            issue.get("tool", ""),
            issue.get("type", ""),
            issue.get("description", ""),
            issue.get("contract", "")
        )

        if key not in seen:
            seen.add(key)
            merged.append(issue)
            logger.debug(f"Merged issue: {key[0]} - {key[1]}")
        else:
            logger.debug(f"Duplicate issue skipped: {key[0]} - {key[1]}")

    logger.info(f"Merged {len(all_issues)} issues into {len(merged)} unique issues")
    return merged


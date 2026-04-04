from typing import List
import logging
from config import get_config

logger = logging.getLogger(__name__)


def decide_next_stage(risk_level: str) -> List[str]:
    """
    Decide which analysis tools to run based on the risk level.

    This decision engine uses configurable rules to determine the appropriate
    depth of analysis based on the assessed risk level.

    Args:
        risk_level (str): Risk level from ML model ("HIGH", "MEDIUM", "LOW")

    Returns:
        List[str]: List of tools to execute next

    Raises:
        ValueError: If risk_level is not one of "HIGH", "MEDIUM", "LOW"

    Example:
        >>> decide_next_stage("HIGH")
        ["Mythril", "Echidna"]
        >>> decide_next_stage("LOW")
        ["Slither"]
    """
    if not isinstance(risk_level, str):
        raise ValueError("Risk level must be a string")

    config = get_config()
    risk_level = risk_level.upper().strip()  # normalize input

    if risk_level not in config.analysis.decision_rules:
        logger.warning(f"Unknown risk level: {risk_level}, defaulting to MEDIUM")
        risk_level = "MEDIUM"

    tools = config.analysis.decision_rules[risk_level]

    logger.debug(f"Decision for risk level '{risk_level}': {tools}")
    return tools

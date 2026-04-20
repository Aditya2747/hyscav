from typing import List
import logging
from config import get_config

logger = logging.getLogger(__name__)


def decide_next_stage(risk_level: str) -> List[str]:
    """
    Decide which analysis tools to run based on the risk level.
    """
    risk_level = risk_level.upper().strip()
    
    config_tools = get_config().analysis.decision_rules.get(risk_level, ['Slither'])
    
    logger.debug(f"Decision for '{risk_level}': {config_tools}")
    return config_tools

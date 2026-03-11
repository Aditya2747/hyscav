"""
Pipeline Orchestrator for HySCAV Hybrid Smart Contract Analyzer.

This module provides the main orchestration class for running the complete
analysis pipeline, including static analysis, feature extraction, ML-based
risk scoring, decision making, and deep analysis with multiple tools.
"""

import logging
import os
from typing import Dict, List, Any, Optional

from analyzers.slither_runner import run_slither, simplify_slither_issues
from analyzers.mythril_runner import run_mythril, simplify_mythril_issues
from analyzers.echidna_runner import run_echidna, simplify_echidna_issues
from controller.feature_extractor import extract_slither_features
from controller.decision_engine import decide_next_stage
from controller.merger import merge_issues
from ml.risk_model import predict_risk
from reports.report_generator import generate_report
from config import get_config

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Orchestrates the complete HySCAV analysis pipeline.
    
    This class manages the sequential execution of analysis stages,
    including static analysis, feature extraction, ML-based risk
    scoring, decision making, and deep analysis with multiple tools.
    
    Attributes:
        config: Configuration settings for the pipeline
        
    Example:
        >>> orchestrator = PipelineOrchestrator()
        >>> result = orchestrator.run_full_pipeline("contracts/Bank.sol")
        >>> print(result)
        True
    """
    
    def __init__(self, config: Optional[Any] = None):
        """
        Initialize the pipeline orchestrator.
        
        Args:
            config: Optional configuration object. If not provided,
                   uses the global configuration from get_config()
        """
        self.config = config if config is not None else get_config()
        logger.info("PipelineOrchestrator initialized")
    
    def run_full_pipeline(self, contract_path: str) -> bool:
        """
        Execute the complete hybrid analysis pipeline.
        
        This method runs all stages of the analysis pipeline:
        1. Static analysis with Slither
        2. Feature extraction
        3. ML-based risk scoring
        4. Decision engine for tool selection
        5. Deep analysis with Mythril and/or Echidna
        6. Issue merging and report generation
        
        Args:
            contract_path (str): Path to the Solidity contract file
            
        Returns:
            bool: True if analysis completed successfully
            
        Raises:
            FileNotFoundError: If the contract file does not exist
            ValueError: If the contract path is invalid
        """
        # Input validation
        if not contract_path or not isinstance(contract_path, str):
            raise ValueError("Contract path must be a non-empty string")
        
        if not contract_path.endswith('.sol'):
            raise ValueError("Invalid contract path. Must be a .sol file.")
        
        if not os.path.exists(contract_path):
            raise FileNotFoundError(f"Contract file not found: {contract_path}")
        
        logger.info("Starting hybrid analysis pipeline")
        logger.info(f"Contract: {contract_path}")
        
        all_issues: List[Dict[str, Any]] = []
        
        # -------------------------------
        # 1. Static Analysis (Slither)
        # -------------------------------
        logger.info("Phase 1: Running static analysis with Slither")
        slither_data: Optional[Dict[str, Any]] = run_slither(contract_path)
        if slither_data is None:
            logger.warning("Slither analysis failed, proceeding with empty results")
            slither_data = {}
        
        slither_issues: List[Dict[str, Any]] = simplify_slither_issues(slither_data)
        all_issues.extend(slither_issues)
        logger.info(f"Slither found {len(slither_issues)} issues")
        
        # -------------------------------
        # 2. Feature Extraction
        # -------------------------------
        logger.info("Phase 2: Extracting features from static analysis")
        features: Dict[str, Any] = extract_slither_features(slither_data)
        logger.info(f"Static features extracted: {features}")
        
        # -------------------------------
        # 3. ML Risk Scoring
        # -------------------------------
        logger.info("Phase 3: Performing ML-based risk assessment")
        risk_level: str
        risk_score: float
        risk_level, risk_score = predict_risk(features)
        logger.info(f"Risk Level: {risk_level} (score = {risk_score})")
        
        # -------------------------------
        # 4. Decision Engine
        # -------------------------------
        logger.info("Phase 4: Determining next analysis tools")
        next_tools: List[str] = decide_next_stage(risk_level)
        logger.info(f"Next analysis tools: {next_tools}")
        
        # -------------------------------
        # 5. Symbolic Analysis (Mythril)
        # -------------------------------
        if "Mythril" in next_tools:
            logger.info("Phase 5a: Launching Mythril symbolic analysis")
            mythril_data: Optional[Dict[str, Any]] = run_mythril(contract_path)
            if mythril_data is not None:
                mythril_issues: List[Dict[str, Any]] = simplify_mythril_issues(mythril_data)
                all_issues.extend(mythril_issues)
                logger.info(f"Mythril found {len(mythril_issues)} issues")
            else:
                logger.warning("Mythril analysis failed")
        
        # -------------------------------
        # 6. Fuzzing Analysis (Echidna)
        # -------------------------------
        if "Echidna" in next_tools:
            logger.info("Phase 5b: Launching Echidna fuzzing analysis")
            echidna_data: Optional[Dict[str, Any]] = run_echidna(contract_path)
            if echidna_data is not None:
                echidna_issues: List[Dict[str, Any]] = simplify_echidna_issues(echidna_data)
                all_issues.extend(echidna_issues)
                logger.info(f"Echidna found {len(echidna_issues)} issues")
            else:
                logger.warning("Echidna analysis failed")
        
        # -------------------------------
        # 7. Issue Merging and Report Generation
        # -------------------------------
        logger.info("Phase 6: Merging issues and generating report")
        final_issues: List[Dict[str, Any]] = merge_issues(all_issues)
        
        report_path: str = generate_report(
            contract_path,
            features,
            risk_level,
            risk_score,
            next_tools,
            final_issues
        )
        logger.info(f"Report saved to: {report_path}")
        
        logger.info("Hybrid analysis completed successfully")
        return True
    
    def run_static_only(self, contract_path: str) -> Dict[str, Any]:
        """
        Run only static analysis (Slither) without deep analysis.
        
        This is a faster option for quick vulnerability scanning.
        
        Args:
            contract_path (str): Path to the Solidity contract file
            
        Returns:
            Dict containing static analysis results and features
        """
        logger.info("Running static analysis only")
        
        slither_data = run_slither(contract_path)
        slither_issues = simplify_slither_issues(slither_data or {})
        features = extract_slither_features(slither_data or {})
        
        return {
            "issues": slither_issues,
            "features": features,
            "tool": "Slither"
        }
    
    def get_risk_assessment(self, contract_path: str) -> Dict[str, Any]:
 """
        Get only the risk assessment without running deep analysis.
        
        Args:
            contract_path (str): Path to the Solidity contract file
            
        Returns:
            Dict containing risk level and score
        """
        logger.info("Running risk assessment only")
        
        slither_data = run_slither(contract_path)
        features = extract_slither_features(slither_data or {})
        risk_level, risk_score = predict_risk(features)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "features": features
        }

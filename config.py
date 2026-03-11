"""
Configuration management for HySCAV hybrid smart contract analyzer.

This module centralizes all configuration settings, thresholds, and tool parameters
to enable easy experimentation and reproducibility for dissertation research.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import os
import json


@dataclass
class AnalysisConfig:
    """Configuration for analysis pipeline behavior."""

    # Risk scoring thresholds
    risk_thresholds: Dict[str, float] = None

    # Tool execution settings
    tool_timeouts: Dict[str, int] = None  # seconds

    # Decision engine settings
    decision_rules: Dict[str, List[str]] = None

    # Output settings
    output_formats: List[str] = None

    def __post_init__(self):
        if self.risk_thresholds is None:
            self.risk_thresholds = {
                "HIGH": 6.0,
                "MEDIUM": 3.0,
                "LOW": 0.0
            }

        if self.tool_timeouts is None:
            self.tool_timeouts = {
                "slither": 300,   # 5 minutes
                "mythril": 600,   # 10 minutes
                "echidna": 1800   # 30 minutes
            }

        if self.decision_rules is None:
            self.decision_rules = {
                "HIGH": ["Mythril", "Echidna"],
                "MEDIUM": ["Mythril", "Echidna"],
                "LOW": ["Slither"]
            }

        if self.output_formats is None:
            self.output_formats = ["json"]


@dataclass
class MLConfig:
    """Configuration for machine learning components."""

    # Feature weights for risk scoring
    feature_weights: Dict[str, float] = None

    # Model parameters (for future ML models)
    model_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.feature_weights is None:
            self.feature_weights = {
                "high": 3.0,
                "medium": 2.0,
                "low": 1.0
            }

        if self.model_params is None:
            self.model_params = {
                "model_type": "rule_based",
                "normalize_features": True
            }


@dataclass
class LoggingConfig:
    """Configuration for logging behavior."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_logging: bool = False
    log_file: str = "hyscav.log"


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    output_dir: str = "reports"
    include_timestamp: bool = True
    compress_reports: bool = False
    export_formats: List[str] = None

    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["json"]


class HySCAVConfig:
    """Main configuration class for HySCAV."""

    def __init__(self):
        self.analysis = AnalysisConfig()
        self.ml = MLConfig()
        self.logging = LoggingConfig()
        self.report = ReportConfig()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'HySCAVConfig':
        """Create configuration from dictionary."""
        config = cls()

        if 'analysis' in config_dict:
            config.analysis = AnalysisConfig(**config_dict['analysis'])
        if 'ml' in config_dict:
            config.ml = MLConfig(**config_dict['ml'])
        if 'logging' in config_dict:
            config.logging = LoggingConfig(**config_dict['logging'])
        if 'report' in config_dict:
            config.report = ReportConfig(**config_dict['report'])

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'analysis': {
                'risk_thresholds': self.analysis.risk_thresholds,
                'tool_timeouts': self.analysis.tool_timeouts,
                'decision_rules': self.analysis.decision_rules,
                'output_formats': self.analysis.output_formats
            },
            'ml': {
                'feature_weights': self.ml.feature_weights,
                'model_params': self.ml.model_params
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_logging': self.logging.file_logging,
                'log_file': self.logging.log_file
            },
            'report': {
                'output_dir': self.report.output_dir,
                'include_timestamp': self.report.include_timestamp,
                'compress_reports': self.report.compress_reports,
                'export_formats': self.report.export_formats
            }
        }


# Global configuration instance
_config = None

def get_config() -> HySCAVConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = HySCAVConfig()
    return _config

def set_config(config: HySCAVConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config

def load_config_from_file(filepath: str) -> HySCAVConfig:
    """Load configuration from JSON file."""
    import json

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)

    config = HySCAVConfig.from_dict(config_dict)
    set_config(config)
    return config

def save_config_to_file(config: HySCAVConfig, filepath: str) -> None:
    """Save configuration to JSON file."""
    config_dict = config.to_dict()

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2)

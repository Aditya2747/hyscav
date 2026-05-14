"""
Echidna runner module for HySCAV.

This module re-exports the robust Docker-native-static-fallback runner
from echidna_runner_docker.py to maintain backward compatibility.
All new code should import directly from analyzers.echidna_runner_docker.
"""

from analyzers.echidna_runner_docker import (
    run_echidna,
    simplify_echidna_issues,
    _detect_echidna_mode,
    _extract_contract_names,
    _find_project_dir,
)

__all__ = ["run_echidna", "simplify_echidna_issues"]


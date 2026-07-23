"""AgeGate Harms simulation and evidence package."""

from .evidence import coverage_report, load_evidence, validate_evidence_registry
from .model import (
    KEY_METRICS,
    calculate_outcomes,
    deterministic_comparison,
    load_config,
    run_monte_carlo,
    sensitivity_analysis,
    summarize_simulations,
)
from .priorities import build_evidence_priorities

__version__ = "0.2.0"

__all__ = [
    "KEY_METRICS",
    "build_evidence_priorities",
    "calculate_outcomes",
    "coverage_report",
    "deterministic_comparison",
    "load_config",
    "load_evidence",
    "run_monte_carlo",
    "sensitivity_analysis",
    "summarize_simulations",
    "validate_evidence_registry",
]

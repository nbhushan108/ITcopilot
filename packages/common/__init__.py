"""Shared utilities and domain primitives for ITcopilot packages."""

from common.constants import ASSESSMENT_YEARS, INDIAN_FINANCIAL_YEAR_PATTERN
from common.types import PAN, Money

__all__ = [
    "ASSESSMENT_YEARS",
    "INDIAN_FINANCIAL_YEAR_PATTERN",
    "PAN",
    "Money",
    "__version__",
]

__version__ = "0.1.0"

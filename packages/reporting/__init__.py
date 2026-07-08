"""Tax report generation module."""

from reporting.generator import ReportGenerator
from reporting.models import TaxReport
from reporting.templates import ITRSummaryTemplate


__all__ = [
    "ITRSummaryTemplate",
    "ReportGenerator",
    "TaxReport",
    "__version__",
]

__version__ = "0.1.0"

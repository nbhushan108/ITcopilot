"""Income tax computation engine for India."""

from tax_engine.calculator import TaxCalculator
from tax_engine.models import IncomeBreakdown, TaxComputationResult, TaxRegime
from tax_engine.slabs import NEW_REGIME_SLABS, OLD_REGIME_SLABS


__all__ = [
    "NEW_REGIME_SLABS",
    "OLD_REGIME_SLABS",
    "IncomeBreakdown",
    "TaxCalculator",
    "TaxComputationResult",
    "TaxRegime",
    "__version__",
]

__version__ = "0.1.0"

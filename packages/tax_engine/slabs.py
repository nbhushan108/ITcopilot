"""Income tax slab definitions for Indian tax regimes."""

from decimal import Decimal

from tax_engine.models import TaxSlabBreakdown

TaxSlab = tuple[Decimal, Decimal | None, Decimal]

OLD_REGIME_SLABS: tuple[TaxSlab, ...] = (
    (Decimal("0"), Decimal("250000"), Decimal("0")),
    (Decimal("250000"), Decimal("500000"), Decimal("0.05")),
    (Decimal("500000"), Decimal("1000000"), Decimal("0.20")),
    (Decimal("1000000"), None, Decimal("0.30")),
)

NEW_REGIME_SLABS: tuple[TaxSlab, ...] = (
    (Decimal("0"), Decimal("400000"), Decimal("0")),
    (Decimal("400000"), Decimal("800000"), Decimal("0.05")),
    (Decimal("800000"), Decimal("1200000"), Decimal("0.10")),
    (Decimal("1200000"), Decimal("1600000"), Decimal("0.15")),
    (Decimal("1600000"), Decimal("2000000"), Decimal("0.20")),
    (Decimal("2000000"), Decimal("2400000"), Decimal("0.25")),
    (Decimal("2400000"), None, Decimal("0.30")),
)

CESS_RATE = Decimal("0.04")

SURCHARGE_THRESHOLDS: tuple[tuple[Decimal, Decimal], ...] = (
    (Decimal("5000000"), Decimal("0.10")),
    (Decimal("10000000"), Decimal("0.15")),
    (Decimal("20000000"), Decimal("0.25")),
    (Decimal("50000000"), Decimal("0.37")),
)


def compute_slab_tax(
    taxable_income: Decimal,
    slabs: tuple[TaxSlab, ...],
) -> tuple[Decimal, list[TaxSlabBreakdown]]:
    """Compute tax based on progressive slab rates.

    Args:
        taxable_income: Net taxable income after deductions.
        slabs: Tuple of (lower, upper, rate) slab definitions.

    Returns:
        Tuple of total base tax and per-slab breakdown.
    """
    total_tax = Decimal("0")
    breakdown: list[TaxSlabBreakdown] = []

    for lower, upper, rate in slabs:
        if taxable_income <= lower:
            breakdown.append(
                TaxSlabBreakdown(
                    lower_limit=lower,
                    upper_limit=upper,
                    rate=rate,
                    taxable_amount=Decimal("0"),
                    tax_amount=Decimal("0"),
                ),
            )
            continue

        slab_upper = upper if upper is not None else taxable_income
        taxable_in_slab = min(taxable_income, slab_upper) - lower
        if taxable_in_slab < 0:
            taxable_in_slab = Decimal("0")

        slab_tax = (taxable_in_slab * rate).quantize(Decimal("0.01"))
        total_tax += slab_tax

        breakdown.append(
            TaxSlabBreakdown(
                lower_limit=lower,
                upper_limit=upper,
                rate=rate,
                taxable_amount=taxable_in_slab,
                tax_amount=slab_tax,
            ),
        )

    return total_tax, breakdown


def compute_surcharge(taxable_income: Decimal, base_tax: Decimal) -> Decimal:
    """Compute surcharge based on taxable income thresholds.

    Args:
        taxable_income: Net taxable income.
        base_tax: Base tax before surcharge.

    Returns:
        Surcharge amount.
    """
    surcharge_rate = Decimal("0")
    for threshold, rate in SURCHARGE_THRESHOLDS:
        if taxable_income > threshold:
            surcharge_rate = rate

    return (base_tax * surcharge_rate).quantize(Decimal("0.01"))

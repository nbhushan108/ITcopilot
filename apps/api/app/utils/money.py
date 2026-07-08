"""Monetary value utility functions."""

from decimal import ROUND_HALF_UP, Decimal


def round_money(value: Decimal, places: int = 2) -> Decimal:
    """Round a monetary value to the specified decimal places.

    Args:
        value: Decimal value to round.
        places: Number of decimal places (default 2).

    Returns:
        Rounded Decimal value.
    """
    quantizer = Decimal(10) ** -places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


def format_inr(value: Decimal) -> str:
    """Format a decimal value as Indian Rupees string.

    Args:
        value: Monetary amount in INR.

    Returns:
        Formatted INR string e.g. '₹1,23,456.78'.
    """
    rounded = round_money(value)
    integer_part, _, decimal_part = f"{rounded:.2f}".partition(".")
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups: list[str] = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        formatted_integer = ",".join([*groups, last_three])
    else:
        formatted_integer = integer_part
    return f"₹{formatted_integer}.{decimal_part}"

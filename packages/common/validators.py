"""Common validation utilities."""

import re
from decimal import Decimal, InvalidOperation

from loguru import logger

from common.constants import INDIAN_FINANCIAL_YEAR_PATTERN


def is_valid_assessment_year(year: str) -> bool:
    """Check if the given string is a valid assessment year format.

    Args:
        year: Assessment year string e.g. '2025-26'.

    Returns:
        True if valid format, False otherwise.
    """
    if not INDIAN_FINANCIAL_YEAR_PATTERN.match(year):
        return False
    start_year_str, end_suffix = year.split("-")
    try:
        start_year = int(start_year_str)
        expected_suffix = str(start_year + 1)[-2:]
        return end_suffix == expected_suffix
    except ValueError:
        return False


def parse_decimal(value: str | int | float | Decimal) -> Decimal:
    """Safely parse a value to Decimal.

    Args:
        value: Input value to parse.

    Returns:
        Parsed Decimal value.

    Raises:
        ValueError: If value cannot be parsed as Decimal.
    """
    try:
        if isinstance(value, str):
            cleaned = re.sub(r"[₹,\s]", "", value.strip())
            return Decimal(cleaned)
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        logger.warning("Failed to parse decimal value '{}': {}", value, exc)
        raise ValueError(f"Invalid decimal value: {value}") from exc


def mask_pan(pan: str) -> str:
    """Mask a PAN for logging purposes.

    Args:
        pan: Full PAN string.

    Returns:
        Masked PAN e.g. 'ABCD****F'.
    """
    if len(pan) < 10:
        return "****"
    return pan[:4] + "****" + pan[-1]

"""Shared type definitions and value objects."""

import re
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, Field


PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


def validate_pan(value: str) -> str:
    """Validate and normalize a PAN string.

    Args:
        value: Raw PAN input.

    Returns:
        Uppercase normalized PAN.

    Raises:
        ValueError: If PAN format is invalid.
    """
    normalized = value.upper().strip()
    if not PAN_PATTERN.match(normalized):
        raise ValueError(f"Invalid PAN format: {value}")
    return normalized


PAN = Annotated[str, AfterValidator(validate_pan)]
Money = Annotated[Decimal, Field(ge=0, decimal_places=2)]

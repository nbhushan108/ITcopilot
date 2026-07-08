"""Type definitions for the ITcopilot configuration engine."""

from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

type LogLevel = Literal[
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

type TaxRegimeName = Literal["old", "new"]


class Environment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ResidentStatus(StrEnum):
    """Indian income tax resident classification."""

    RESIDENT = "resident"
    NON_RESIDENT = "non_resident"
    RESIDENT_NOT_ORDINARILY_RESIDENT = "rnor"


class TaxRegime(StrEnum):
    """Income tax regime selection."""

    OLD = "old"
    NEW = "new"


class TaxSlabDefinition(BaseModel):
    """Single progressive tax slab definition."""

    lower: Decimal
    upper: Decimal | None
    rate: Decimal

    model_config = {"frozen": True}


class SurchargeThreshold(BaseModel):
    """Income threshold and surcharge rate pair."""

    threshold: Decimal
    rate: Decimal

    model_config = {"frozen": True}

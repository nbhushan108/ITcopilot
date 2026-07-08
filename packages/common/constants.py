"""Shared constants for ITcopilot."""

import re


INDIAN_FINANCIAL_YEAR_PATTERN = re.compile(r"^\d{4}-\d{2}$")

ASSESSMENT_YEARS: tuple[str, ...] = (
    "2023-24",
    "2024-25",
    "2025-26",
)

STANDARD_DEDUCTION_OLD_REGIME: int = 50000
STANDARD_DEDUCTION_NEW_REGIME: int = 75000

SECTION_80C_LIMIT: int = 150000

PAN_LENGTH: int = 10

MAX_UPLOAD_SIZE_MB: int = 50

SUPPORTED_BROKERS: tuple[str, ...] = (
    "zerodha",
    "groww",
    "upstox",
    "icici_direct",
    "hdfc_securities",
)

SUPPORTED_FILE_EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".xlsx",
    ".xls",
    ".csv",
)

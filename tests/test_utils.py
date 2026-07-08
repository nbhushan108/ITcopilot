"""Application utility unit tests."""

from decimal import Decimal

import pytest

from app.utils.datetime_utils import utc_now
from app.utils.money import format_inr, round_money


@pytest.mark.unit
class TestMoneyUtils:
    """Tests for monetary utility functions."""

    def test_round_money(self) -> None:
        """round_money should round to two decimal places."""
        assert round_money(Decimal("123.456")) == Decimal("123.46")

    def test_format_inr(self) -> None:
        """format_inr should format Indian numbering."""
        formatted = format_inr(Decimal("123456.78"))
        assert formatted.startswith("₹")
        assert "23,456.78" in formatted

    def test_format_inr_small_amount(self) -> None:
        """format_inr should handle amounts under 1000 without grouping."""
        assert format_inr(Decimal("999.50")) == "₹999.50"


@pytest.mark.unit
class TestDatetimeUtils:
    """Tests for datetime utilities."""

    def test_utc_now_has_timezone(self) -> None:
        """utc_now should return timezone-aware datetime."""
        now = utc_now()
        assert now.tzinfo is not None

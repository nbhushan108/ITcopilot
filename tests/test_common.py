"""Common utilities unit tests."""

import pytest

from common.types import validate_pan
from common.validators import is_valid_assessment_year, mask_pan, parse_decimal


@pytest.mark.unit
class TestValidators:
    """Unit tests for common validators."""

    def test_valid_assessment_year(self) -> None:
        """Valid assessment years should pass validation."""
        assert is_valid_assessment_year("2025-26") is True
        assert is_valid_assessment_year("2024-25") is True

    def test_invalid_assessment_year(self) -> None:
        """Invalid assessment years should fail validation."""
        assert is_valid_assessment_year("2025-27") is False
        assert is_valid_assessment_year("invalid") is False

    def test_parse_decimal_from_string(self) -> None:
        """Should parse formatted currency strings."""
        assert parse_decimal("₹1,23,456.78") == parse_decimal("123456.78")

    def test_parse_decimal_invalid(self) -> None:
        """Invalid decimal strings should raise ValueError."""
        with pytest.raises(ValueError):
            parse_decimal("not-a-number")

    def test_mask_pan(self) -> None:
        """PAN should be masked for logging."""
        assert mask_pan("ABCDE1234F") == "ABCD****F"
        assert mask_pan("SHORT") == "****"

    def test_invalid_assessment_year_value_error(self) -> None:
        """Malformed year suffix should return False."""
        assert is_valid_assessment_year("abcd-ef") is False


@pytest.mark.unit
class TestCommonTypes:
    """Tests for shared type validators."""

    def test_validate_pan_success(self) -> None:
        """Valid PAN should normalize to uppercase."""
        assert validate_pan("abcde1234f") == "ABCDE1234F"

    def test_validate_pan_invalid(self) -> None:
        """Invalid PAN should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid PAN format"):
            validate_pan("INVALID-PAN")

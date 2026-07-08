"""Broker imports package smoke tests."""

from decimal import Decimal
from pathlib import Path

import pytest

from broker_imports.registry import get_broker_registry
from broker_imports.zerodha import ZerodhaImporter


SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.mark.unit
class TestZerodhaImporter:
    """Tests for Zerodha broker importer."""

    def test_import_sample_tradebook(self) -> None:
        """Zerodha importer should parse sample tradebook CSV."""
        importer = ZerodhaImporter()
        statement = importer.import_statement(SAMPLE_DIR / "zerodha_tradebook_sample.csv")
        assert statement.broker == "zerodha"
        assert len(statement.trades) == 5
        assert statement.total_turnover > Decimal("0")

    def test_import_uses_parser_registry(self) -> None:
        """Zerodha importer should route CSV through parser registry."""
        importer = ZerodhaImporter()
        statement = importer.import_statement(SAMPLE_DIR / "zerodha_tradebook_sample.csv")
        assert all(trade.symbol for trade in statement.trades)


@pytest.mark.unit
class TestBrokerRegistry:
    """Tests for broker registry."""

    def test_supported_brokers(self) -> None:
        """Registry should list zerodha as supported broker."""
        registry = get_broker_registry()
        assert "zerodha" in registry.supported_brokers

    def test_import_via_registry(self) -> None:
        """Registry should import Zerodha statement."""
        registry = get_broker_registry()
        statement = registry.import_statement(
            "zerodha",
            SAMPLE_DIR / "zerodha_tradebook_sample.csv",
        )
        assert statement.broker == "zerodha"

    def test_unsupported_broker(self) -> None:
        """Registry should reject unknown brokers."""
        registry = get_broker_registry()
        with pytest.raises(ValueError, match="Unsupported broker"):
            registry.import_statement("unknown_broker", SAMPLE_DIR / "zerodha_tradebook_sample.csv")

    def test_import_with_parse_errors(self, tmp_path: Path) -> None:
        """Importer should fail when parser reports errors."""
        from unittest.mock import patch

        from parsers.base import ParseResult

        bad_result = ParseResult(
            source_file="bad.csv",
            parser_name="csv_parser",
            errors=["parse failed"],
        )
        importer = ZerodhaImporter()
        with patch("broker_imports.zerodha.get_parser_registry") as mock_registry:
            mock_registry.return_value.parse.return_value = bad_result
            with pytest.raises(ValueError, match="parse failed"):
                importer.import_statement(tmp_path / "bad.csv")

    def test_skip_invalid_rows(self) -> None:
        """Importer should skip malformed rows without failing."""
        from unittest.mock import patch

        from broker_imports.base import TradeRecord
        from parsers.base import ParseResult

        importer = ZerodhaImporter()
        valid_trade = TradeRecord(
            trade_date=__import__("datetime").date(2024, 1, 1),
            symbol="INFY",
            exchange="NSE",
            transaction_type="BUY",
            quantity=1,
            price=Decimal("100"),
            amount=Decimal("100"),
            charges=Decimal("1"),
        )
        mixed_result = ParseResult(
            source_file="mixed.csv",
            parser_name="csv_parser",
            records=[{"row": 1}, {"row": 2}],
        )
        with patch("broker_imports.zerodha.get_parser_registry") as mock_registry:
            mock_registry.return_value.parse.return_value = mixed_result
            with patch.object(
                importer,
                "_parse_row",
                side_effect=[valid_trade, ValueError("bad row")],
            ):
                statement = importer.import_statement(SAMPLE_DIR / "zerodha_tradebook_sample.csv")
        assert len(statement.trades) == 1

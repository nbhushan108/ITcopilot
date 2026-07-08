"""Zerodha broker statement importer."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from loguru import logger

from broker_imports.base import BaseBrokerImporter, BrokerStatement, TradeRecord
from parsers.registry import get_parser_registry


class ZerodhaImporter(BaseBrokerImporter):
    """Importer for Zerodha tradebook and P&L CSV exports."""

    @property
    def broker_name(self) -> str:
        """Return broker identifier."""
        return "zerodha"

    def import_statement(self, file_path: Path) -> BrokerStatement:
        """Import a Zerodha CSV tradebook export via the parser registry.

        Args:
            file_path: Path to Zerodha CSV export file.

        Returns:
            Parsed BrokerStatement with trade records.
        """
        logger.info("Importing Zerodha statement: {}", file_path.name)

        try:
            parse_result = get_parser_registry().parse(file_path)
            if parse_result.errors:
                raise ValueError("; ".join(parse_result.errors))

            trades: list[TradeRecord] = []
            total_turnover = Decimal("0")
            total_charges = Decimal("0")
            client_id = "unknown"

            for row in parse_result.records:
                if not isinstance(row, dict):
                    continue
                try:
                    trade = self._parse_row(row)
                    trades.append(trade)
                    total_turnover += trade.amount
                    total_charges += trade.charges
                except (KeyError, ValueError, TypeError) as exc:
                    logger.warning("Skipping invalid row: {}", exc)

            if parse_result.records and isinstance(parse_result.records[0], dict):
                client_id = str(parse_result.records[0].get("Client ID", "unknown"))

            period_start = min((t.trade_date for t in trades), default=date.today())
            period_end = max((t.trade_date for t in trades), default=date.today())

            return BrokerStatement(
                broker=self.broker_name,
                client_id=client_id,
                period_start=period_start,
                period_end=period_end,
                trades=trades,
                total_turnover=total_turnover,
                total_charges=total_charges,
            )

        except Exception as exc:
            logger.error("Zerodha import failed: {}", exc)
            raise ValueError(f"Failed to import Zerodha statement: {exc}") from exc

    def _parse_row(self, row: dict[str, object]) -> TradeRecord:
        """Parse a single CSV row into a TradeRecord.

        Args:
            row: Dictionary representing a CSV row.

        Returns:
            Parsed TradeRecord.
        """
        trade_date_str = str(row.get("Trade Date", row.get("Date", "")))
        trade_date = date.fromisoformat(trade_date_str) if trade_date_str else date.today()

        quantity_raw = row.get("Quantity", 0)
        quantity = int(quantity_raw) if isinstance(quantity_raw, (int, float, str)) else 0

        return TradeRecord(
            trade_date=trade_date,
            symbol=str(row.get("Symbol", row.get("Instrument", ""))),
            exchange=str(row.get("Exchange", "NSE")),
            transaction_type=str(row.get("Trade Type", row.get("Type", "BUY"))),
            quantity=quantity,
            price=Decimal(str(row.get("Price", 0))),
            amount=Decimal(str(row.get("Amount", 0))),
            charges=Decimal(str(row.get("Total Charges", row.get("Charges", 0)))),
        )

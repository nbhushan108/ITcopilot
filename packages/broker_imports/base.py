"""Base broker import interface and models."""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field


class TradeRecord(BaseModel):
    """Individual trade record from a broker statement."""

    trade_date: date
    symbol: str
    exchange: str = "NSE"
    transaction_type: str
    quantity: int = Field(ge=0)
    price: Decimal = Field(ge=0)
    amount: Decimal
    charges: Decimal = Field(default=Decimal("0"))


class BrokerStatement(BaseModel):
    """Parsed broker statement with trade records."""

    broker: str
    client_id: str
    period_start: date
    period_end: date
    trades: list[TradeRecord] = Field(default_factory=list)
    total_turnover: Decimal = Field(default=Decimal("0"))
    total_charges: Decimal = Field(default=Decimal("0"))


class BaseBrokerImporter(ABC):
    """Abstract base class for broker statement importers."""

    @property
    @abstractmethod
    def broker_name(self) -> str:
        """Return broker identifier."""

    @abstractmethod
    def import_statement(self, file_path: Path) -> BrokerStatement:
        """Import and parse a broker statement file.

        Args:
            file_path: Path to the broker statement file.

        Returns:
            Parsed BrokerStatement.
        """

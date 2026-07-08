"""Broker importer registry."""

from pathlib import Path

from loguru import logger

from broker_imports.base import BaseBrokerImporter, BrokerStatement
from broker_imports.zerodha import ZerodhaImporter


class BrokerRegistry:
    """Registry for broker statement importers."""

    def __init__(self) -> None:
        """Initialize with default broker importers."""
        self._importers: dict[str, BaseBrokerImporter] = {}
        self.register(ZerodhaImporter())

    def register(self, importer: BaseBrokerImporter) -> None:
        """Register a broker importer.

        Args:
            importer: Broker importer instance.
        """
        self._importers[importer.broker_name] = importer
        logger.debug("Registered broker importer: {}", importer.broker_name)

    def get_importer(self, broker_name: str) -> BaseBrokerImporter | None:
        """Get importer by broker name.

        Args:
            broker_name: Broker identifier.

        Returns:
            Matching importer or None.
        """
        return self._importers.get(broker_name.lower())

    def import_statement(self, broker_name: str, file_path: Path) -> BrokerStatement:
        """Import a broker statement using the named importer.

        Args:
            broker_name: Broker identifier.
            file_path: Path to statement file.

        Returns:
            Parsed BrokerStatement.

        Raises:
            ValueError: If broker is not supported.
        """
        importer = self.get_importer(broker_name)
        if importer is None:
            raise ValueError(f"Unsupported broker: {broker_name}")
        return importer.import_statement(file_path)

    @property
    def supported_brokers(self) -> list[str]:
        """Return list of supported broker names."""
        return list(self._importers.keys())


_registry: BrokerRegistry | None = None


def get_broker_registry() -> BrokerRegistry:
    """Return singleton broker registry."""
    global _registry
    if _registry is None:
        _registry = BrokerRegistry()
    return _registry

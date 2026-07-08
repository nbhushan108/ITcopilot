"""Base parser interface and result models."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ParseResult(BaseModel):
    """Result of a document parsing operation."""

    source_file: str
    parser_name: str
    record_count: int = 0
    records: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return True if parsing completed without errors."""
        return len(self.errors) == 0


class BaseParser(ABC):
    """Abstract base class for all document parsers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return parser identifier name."""

    @property
    @abstractmethod
    def supported_extensions(self) -> tuple[str, ...]:
        """Return tuple of supported file extensions."""

    @abstractmethod
    def parse(self, file_path: Path) -> ParseResult:
        """Parse the given file and return structured results.

        Args:
            file_path: Path to the file to parse.

        Returns:
            ParseResult containing extracted records and metadata.
        """

    def supports(self, file_path: Path) -> bool:
        """Check if this parser supports the given file.

        Args:
            file_path: Path to check.

        Returns:
            True if file extension is supported.
        """
        return file_path.suffix.lower() in self.supported_extensions

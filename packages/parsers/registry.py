"""Parser registry for automatic parser selection."""

from pathlib import Path

from loguru import logger

from parsers.base import BaseParser, ParseResult
from parsers.csv_parser import CSVParser
from parsers.pdf_parser import PDFParser


class ParserRegistry:
    """Registry for document parsers with automatic selection."""

    def __init__(self) -> None:
        """Initialize registry with default parsers."""
        self._parsers: dict[str, BaseParser] = {}
        self.register(CSVParser())
        self.register(PDFParser())

    def register(self, parser: BaseParser) -> None:
        """Register a parser instance.

        Args:
            parser: Parser to register.
        """
        self._parsers[parser.name] = parser
        logger.debug("Registered parser: {}", parser.name)

    def get_parser(self, file_path: Path) -> BaseParser | None:
        """Find a suitable parser for the given file.

        Args:
            file_path: Path to the file.

        Returns:
            Matching parser or None if no parser supports the file.
        """
        for parser in self._parsers.values():
            if parser.supports(file_path):
                return parser
        return None

    def parse(self, file_path: Path) -> ParseResult:
        """Parse a file using the appropriate registered parser.

        Args:
            file_path: Path to the file to parse.

        Returns:
            ParseResult from the selected parser.

        Raises:
            ValueError: If no parser supports the file type.
        """
        parser = self.get_parser(file_path)
        if parser is None:
            raise ValueError(f"No parser available for file: {file_path.suffix}")

        return parser.parse(file_path)

    @property
    def available_parsers(self) -> list[str]:
        """Return list of registered parser names."""
        return list(self._parsers.keys())


_registry: ParserRegistry | None = None


def get_parser_registry() -> ParserRegistry:
    """Return singleton parser registry instance."""
    global _registry
    if _registry is None:
        _registry = ParserRegistry()
    return _registry

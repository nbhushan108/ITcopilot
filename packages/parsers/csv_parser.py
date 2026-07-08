"""CSV document parser using Polars."""

from pathlib import Path

import polars as pl
from loguru import logger

from parsers.base import BaseParser, ParseResult


class CSVParser(BaseParser):
    """Parser for CSV financial data files."""

    @property
    def name(self) -> str:
        """Return parser identifier."""
        return "csv_parser"

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Return supported file extensions."""
        return (".csv",)

    def parse(self, file_path: Path) -> ParseResult:
        """Parse a CSV file into structured records.

        Args:
            file_path: Path to the CSV file.

        Returns:
            ParseResult with row records as dictionaries.
        """
        logger.info("Parsing CSV file: {}", file_path.name)
        errors: list[str] = []

        try:
            dataframe = pl.read_csv(file_path, infer_schema_length=1000)
            records = dataframe.to_dicts()
            metadata: dict[str, object] = {
                "columns": dataframe.columns,
                "row_count": dataframe.height,
                "schema": {
                    col: str(dtype)
                    for col, dtype in zip(dataframe.columns, dataframe.dtypes, strict=True)
                },
            }

            return ParseResult(
                source_file=str(file_path),
                parser_name=self.name,
                record_count=len(records),
                records=records,
                metadata=metadata,
            )

        except Exception as exc:
            logger.error("CSV parsing failed for {}: {}", file_path.name, exc)
            errors.append(f"CSV parsing error: {exc}")
            return ParseResult(
                source_file=str(file_path),
                parser_name=self.name,
                errors=errors,
            )

"""PDF document parser using pdfplumber."""

from pathlib import Path

import pdfplumber
from loguru import logger

from parsers.base import BaseParser, ParseResult


class PDFParser(BaseParser):
    """Parser for extracting text and tables from PDF documents."""

    @property
    def name(self) -> str:
        """Return parser identifier."""
        return "pdf_parser"

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Return supported file extensions."""
        return (".pdf",)

    def parse(self, file_path: Path) -> ParseResult:
        """Extract text and tables from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParseResult with extracted page text and table data.
        """
        logger.info("Parsing PDF file: {}", file_path.name)
        records: list[dict[str, object]] = []
        errors: list[str] = []
        metadata: dict[str, object] = {"page_count": 0, "table_count": 0}

        try:
            with pdfplumber.open(file_path) as pdf:
                metadata["page_count"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    tables = page.extract_tables() or []

                    records.append(
                        {
                            "page": page_num,
                            "text": text,
                            "table_count": len(tables),
                        },
                    )

                    for table_idx, table in enumerate(tables):
                        records.append(
                            {
                                "page": page_num,
                                "table_index": table_idx,
                                "rows": table,
                            },
                        )
                        table_count = metadata.get("table_count", 0)
                        if isinstance(table_count, int):
                            metadata["table_count"] = table_count + 1

        except Exception as exc:
            logger.error("PDF parsing failed for {}: {}", file_path.name, exc)
            errors.append(f"PDF parsing error: {exc}")

        return ParseResult(
            source_file=str(file_path),
            parser_name=self.name,
            record_count=len(records),
            records=records,
            metadata=metadata,
            errors=errors,
        )

"""Parser package smoke tests."""

from pathlib import Path

import pytest

from parsers.csv_parser import CSVParser
from parsers.pdf_parser import PDFParser
from parsers.registry import get_parser_registry

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.mark.unit
class TestCSVParser:
    """Tests for CSV parser."""

    def test_parse_sample_csv(self) -> None:
        """CSV parser should parse sample tax computation file."""
        parser = CSVParser()
        result = parser.parse(SAMPLE_DIR / "tax_computation_samples.csv")
        assert result.success
        assert result.record_count > 0
        assert result.parser_name == "csv_parser"


@pytest.mark.unit
class TestParserRegistry:
    """Tests for parser registry."""

    def test_registry_parses_csv(self) -> None:
        """Registry should auto-select CSV parser."""
        registry = get_parser_registry()
        result = registry.parse(SAMPLE_DIR / "zerodha_tradebook_sample.csv")
        assert result.success
        assert result.record_count > 0

    def test_registry_unknown_extension(self) -> None:
        """Registry should reject unknown file types."""
        registry = get_parser_registry()
        with pytest.raises(ValueError, match="No parser available"):
            registry.parse(SAMPLE_DIR / "README.md")


@pytest.mark.unit
class TestPDFParser:
    """Tests for PDF parser."""

    def test_pdf_parser_supports_pdf_extension(self) -> None:
        """PDF parser should declare pdf extension support."""
        parser = PDFParser()
        assert parser.supports(Path("statement.pdf"))
        assert not parser.supports(Path("statement.csv"))

    def test_parse_pdf_with_mocked_pdfplumber(self, tmp_path: Path) -> None:
        """PDF parser should extract page text and tables."""
        from unittest.mock import MagicMock, patch

        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text"
        mock_page.extract_tables.return_value = [[["Header"], ["Value"]]]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None

        parser = PDFParser()
        with patch("parsers.pdf_parser.pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(pdf_path)

        assert result.parser_name == "pdf_parser"
        assert result.record_count > 0
        assert result.metadata["page_count"] == 1

    def test_parse_pdf_failure_returns_errors(self, tmp_path: Path) -> None:
        """PDF parser should capture errors for unreadable files."""
        from unittest.mock import patch

        pdf_path = tmp_path / "broken.pdf"
        pdf_path.write_bytes(b"not-a-pdf")

        parser = PDFParser()
        with patch("parsers.pdf_parser.pdfplumber.open", side_effect=OSError("corrupt")):
            result = parser.parse(pdf_path)

        assert result.errors
        assert result.record_count == 0


@pytest.mark.unit
class TestParserRegistryExtras:
    """Additional parser registry coverage."""

    def test_available_parsers_lists_defaults(self) -> None:
        """Registry should expose default parser names."""
        registry = get_parser_registry()
        assert "csv_parser" in registry.available_parsers
        assert "pdf_parser" in registry.available_parsers

    def test_csv_parser_error_path(self, tmp_path: Path) -> None:
        """CSV parser should return errors for invalid files."""
        bad_file = tmp_path / "bad.csv"
        bad_file.write_text("", encoding="utf-8")
        parser = CSVParser()
        result = parser.parse(bad_file)
        assert result.errors or result.record_count == 0

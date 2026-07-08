"""Excel engine package smoke tests."""

from pathlib import Path

import pytest
from openpyxl import Workbook

from excel_engine.reader import ExcelReader
from excel_engine.writer import ExcelWriter, ReportSheet


@pytest.mark.unit
class TestExcelWriter:
    """Tests for Excel writer."""

    def test_write_report(self, tmp_path: Path) -> None:
        """Excel writer should create a multi-sheet workbook."""
        writer = ExcelWriter()
        output = tmp_path / "report.xlsx"
        sheets = [
            ReportSheet(
                name="Summary",
                headers=["Field", "Value"],
                rows=[["Income", 100000]],
            ),
        ]
        result = writer.write_report(output, sheets)
        assert result.exists()
        assert result.suffix == ".xlsx"


@pytest.mark.unit
class TestExcelReader:
    """Tests for Excel reader."""

    def test_read_and_list_sheets(self, tmp_path: Path) -> None:
        """Excel reader should read sheets written by openpyxl."""
        workbook_path = tmp_path / "data.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        if sheet is not None:
            sheet.title = "Data"
            sheet.append(["Name", "Amount"])
            sheet.append(["Salary", 50000])
        workbook.save(workbook_path)

        reader = ExcelReader()
        sheets = reader.list_sheets(workbook_path)
        assert "Data" in sheets

        dataframe = reader.read_sheet(workbook_path, sheet_name="Data")
        assert dataframe.height == 1
        assert "Name" in dataframe.columns

    def test_read_missing_sheet_raises(self, tmp_path: Path) -> None:
        """Reader should raise when sheet is missing."""
        workbook_path = tmp_path / "data.xlsx"
        workbook = Workbook()
        workbook.save(workbook_path)
        reader = ExcelReader()
        with pytest.raises(ValueError, match="Sheet not found"):
            reader.read_sheet(workbook_path, sheet_name="Missing")

    def test_list_sheets_invalid_file(self, tmp_path: Path) -> None:
        """list_sheets should raise for invalid workbook paths."""
        reader = ExcelReader()
        with pytest.raises(ValueError, match="Failed to read workbook"):
            reader.list_sheets(tmp_path / "missing.xlsx")

    def test_write_report_failure(self, tmp_path: Path) -> None:
        """Writer should raise ValueError when save fails."""
        from unittest.mock import patch

        writer = ExcelWriter()
        with patch("excel_engine.writer.Workbook.save", side_effect=OSError("disk full")):
            with pytest.raises(ValueError, match="Excel write failed"):
                writer.write_report(tmp_path / "fail.xlsx", [])

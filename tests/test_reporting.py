"""Reporting package smoke tests."""

from decimal import Decimal
from pathlib import Path

import pytest

from reporting.generator import ReportGenerator
from reporting.templates import ITRSummaryTemplate
from tax_engine.calculator import TaxCalculator
from tax_engine.models import IncomeBreakdown, TaxRegime


@pytest.mark.unit
class TestReportGenerator:
    """Tests for tax report generator."""

    @pytest.fixture
    def computation_result(self):
        """Provide a sample tax computation result."""
        calculator = TaxCalculator()
        income = IncomeBreakdown(
            gross_salary=Decimal("1200000"),
            section_80c=Decimal("150000"),
            standard_deduction=Decimal("50000"),
        )
        return calculator.compute(
            income=income,
            regime=TaxRegime.OLD,
            assessment_year="2025-26",
        )

    def test_generate_text_report(self, computation_result) -> None:
        """Report generator should produce plain text output."""
        generator = ReportGenerator()
        report = generator.generate(pan="ABCDE1234F", computation=computation_result)
        text = generator.to_text(report)
        assert "Income Tax Report" in text
        assert "ABCD" in text
        assert report.computation.total_tax_payable > 0

    def test_render_excel_template(self, computation_result, tmp_path: Path) -> None:
        """ITR summary template should render Excel report."""
        generator = ReportGenerator()
        report = generator.generate(pan="ABCDE1234F", computation=computation_result)
        template = ITRSummaryTemplate()
        output = tmp_path / "itr_summary.xlsx"
        result = template.render_excel(report, output)
        assert result.exists()

    def test_to_text_handles_non_decimal_amounts(self, computation_result) -> None:
        """Plain text report should render non-decimal row amounts."""
        generator = ReportGenerator()
        report = generator.generate(pan="ABCDE1234F", computation=computation_result)
        report.sections[0].rows.append({"label": "Note", "amount": "N/A"})
        text = generator.to_text(report)
        assert "N/A" in text

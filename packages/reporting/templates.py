"""Report template definitions."""

from pathlib import Path

from excel_engine.writer import ExcelWriter, ReportSheet
from reporting.models import TaxReport


class ITRSummaryTemplate:
    """Template for generating ITR summary Excel reports."""

    def __init__(self) -> None:
        """Initialize template with Excel writer."""
        self._writer = ExcelWriter()

    def render_excel(self, report: TaxReport, output_path: Path) -> Path:
        """Render tax report as Excel workbook.

        Args:
            report: TaxReport to render.
            output_path: Destination file path.

        Returns:
            Path to generated Excel file.
        """
        summary_sheet = ReportSheet(
            name="Summary",
            headers=["Field", "Value"],
            rows=[
                ["Assessment Year", report.assessment_year],
                ["Regime", report.computation.regime.value],
                ["Gross Total Income", float(report.computation.gross_total_income)],
                ["Total Deductions", float(report.computation.total_deductions)],
                ["Taxable Income", float(report.computation.taxable_income)],
                ["Total Tax Payable", float(report.computation.total_tax_payable)],
                ["Effective Tax Rate", f"{report.computation.effective_tax_rate}%"],
            ],
            column_widths={1: 30, 2: 20},
        )

        slab_sheet = ReportSheet(
            name="Slab Breakdown",
            headers=["Slab Range", "Rate", "Taxable Amount", "Tax"],
            rows=[
                [
                    (
                        f"₹{s.lower_limit:,.0f} - "
                        f"{'∞' if s.upper_limit is None else f'₹{s.upper_limit:,.0f}'}"
                    ),
                    f"{s.rate * 100:.0f}%",
                    float(s.taxable_amount),
                    float(s.tax_amount),
                ]
                for s in report.computation.slab_breakdown
            ],
            column_widths={1: 25, 2: 10, 3: 18, 4: 15},
        )

        return self._writer.write_report(output_path, [summary_sheet, slab_sheet])

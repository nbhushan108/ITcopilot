"""Tax report generator."""

from decimal import Decimal

from loguru import logger

from reporting.models import TaxReport, TaxReportSection
from tax_engine.models import TaxComputationResult


class ReportGenerator:
    """Generator for structured tax reports from computation results."""

    def generate(
        self,
        pan: str,
        computation: TaxComputationResult,
    ) -> TaxReport:
        """Generate a complete tax report from computation results.

        Args:
            pan: Taxpayer PAN.
            computation: Tax computation result.

        Returns:
            Structured TaxReport document.
        """
        logger.info(
            "Generating tax report for PAN={} AY={}",
            pan[:4] + "****",
            computation.assessment_year,
        )

        income_section = TaxReportSection(
            title="Income Summary",
            rows=[
                {"label": "Gross Total Income", "amount": computation.gross_total_income},
                {"label": "Total Deductions", "amount": computation.total_deductions},
                {"label": "Taxable Income", "amount": computation.taxable_income},
            ],
        )

        tax_section = TaxReportSection(
            title="Tax Computation",
            rows=[
                {"label": "Base Tax", "amount": computation.base_tax},
                {"label": "Surcharge", "amount": computation.surcharge},
                {"label": "Health & Education Cess (4%)", "amount": computation.cess},
                {"label": "Total Tax Payable", "amount": computation.total_tax_payable},
            ],
            subtotal=computation.total_tax_payable,
        )

        slab_rows = [
            {
                "slab": (
                    f"₹{s.lower_limit:,.0f} - "
                    f"{'∞' if s.upper_limit is None else f'₹{s.upper_limit:,.0f}'}"
                ),
                "rate": f"{s.rate * 100:.0f}%",
                "taxable": s.taxable_amount,
                "tax": s.tax_amount,
            }
            for s in computation.slab_breakdown
        ]

        slab_section = TaxReportSection(
            title="Slab-wise Breakdown",
            rows=slab_rows,
        )

        summary = {
            "regime": computation.regime.value,
            "effective_tax_rate": f"{computation.effective_tax_rate}%",
            "total_tax_payable": computation.total_tax_payable,
        }

        return TaxReport(
            title=f"Income Tax Report - AY {computation.assessment_year}",
            pan=pan,
            assessment_year=computation.assessment_year,
            computation=computation,
            sections=[income_section, tax_section, slab_section],
            summary=summary,
        )

    def to_text(self, report: TaxReport) -> str:
        """Render a tax report as plain text.

        Args:
            report: TaxReport to render.

        Returns:
            Formatted plain text report string.
        """
        lines = [
            "=" * 60,
            report.title,
            f"PAN: {report.pan[:4]}****{report.pan[-1]}",
            f"Generated: {report.generated_at.isoformat()}",
            "=" * 60,
            "",
        ]

        for section in report.sections:
            lines.append(f"--- {section.title} ---")
            for row in section.rows:
                label = row.get("label", row.get("slab", ""))
                amount = row.get("amount", row.get("tax", ""))
                if isinstance(amount, Decimal):
                    lines.append(f"  {label}: ₹{amount:,.2f}")
                else:
                    lines.append(f"  {label}: {amount}")
            if section.subtotal is not None:
                lines.append(f"  Subtotal: ₹{section.subtotal:,.2f}")
            lines.append("")

        lines.append("--- Summary ---")
        for key, value in report.summary.items():
            if isinstance(value, Decimal):
                lines.append(f"  {key}: ₹{value:,.2f}")
            else:
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)

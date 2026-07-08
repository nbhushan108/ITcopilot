"""Initial schema: tax_assessments table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tax_assessments table."""
    op.create_table(
        "tax_assessments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("pan", sa.String(length=10), nullable=False),
        sa.Column("assessment_year", sa.String(length=9), nullable=False),
        sa.Column("regime", sa.String(length=10), nullable=False),
        sa.Column("gross_total_income", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_deductions", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("taxable_income", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("tax_payable", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tax_assessments_pan"), "tax_assessments", ["pan"], unique=False)


def downgrade() -> None:
    """Drop tax_assessments table."""
    op.drop_index(op.f("ix_tax_assessments_pan"), table_name="tax_assessments")
    op.drop_table("tax_assessments")

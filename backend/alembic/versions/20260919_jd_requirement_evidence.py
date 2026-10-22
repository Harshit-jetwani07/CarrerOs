"""Store requirement-level JD evidence.

Revision ID: 20260919_jd_evidence
Revises: 20260918_assistant_msgs
"""
from alembic import op
import sqlalchemy as sa

revision = "20260919_jd_evidence"
down_revision = "20260918_assistant_msgs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("job_descriptions")}
    if "requirement_breakdown" not in columns:
        op.add_column("job_descriptions", sa.Column("requirement_breakdown", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("job_descriptions")}
    if "requirement_breakdown" in columns:
        op.drop_column("job_descriptions", "requirement_breakdown")

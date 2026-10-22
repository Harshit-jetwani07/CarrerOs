"""Allow explicit Resume Builder use in overview.

Revision ID: 20260918_builder_consent
Revises: 20260917_keys_drafts
"""
from alembic import op
import sqlalchemy as sa

revision = "20260918_builder_consent"
down_revision = "20260917_keys_drafts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("resume_drafts")}
    if "use_for_overview" not in columns:
        op.add_column("resume_drafts", sa.Column("use_for_overview", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("resume_drafts")}
    if "use_for_overview" in columns:
        op.drop_column("resume_drafts", "use_for_overview")

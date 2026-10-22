"""Add declared interests for explainable role-fit scoring.

Revision ID: 20260917_add_user_interests
Revises:
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "20260917_add_user_interests"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "interests" not in columns:
        op.add_column("users", sa.Column("interests", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "interests" in columns:
        op.drop_column("users", "interests")

"""Add encrypted user provider keys and editable resume drafts.

Revision ID: 20260917_keys_drafts
Revises: 20260917_add_user_interests
"""
from alembic import op
import sqlalchemy as sa

revision = "20260917_keys_drafts"
down_revision = "20260917_add_user_interests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "user_api_keys" not in tables:
        op.create_table(
            "user_api_keys",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("provider", sa.String(), nullable=False),
            sa.Column("encrypted_key", sa.String(), nullable=False),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("user_id", "provider", name="uq_user_api_key_provider"),
        )
        op.create_index("ix_user_api_keys_user_id", "user_api_keys", ["user_id"])
    if "resume_drafts" not in tables:
        op.create_table(
            "resume_drafts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
            sa.Column("personal_info", sa.JSON(), nullable=True), sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("education", sa.JSON(), nullable=True), sa.Column("skills", sa.JSON(), nullable=True),
            sa.Column("projects", sa.JSON(), nullable=True), sa.Column("experience", sa.JSON(), nullable=True),
            sa.Column("certifications", sa.JSON(), nullable=True), sa.Column("achievements", sa.JSON(), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_resume_drafts_user_id", "resume_drafts", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "resume_drafts" in tables:
        op.drop_table("resume_drafts")
    if "user_api_keys" in tables:
        op.drop_table("user_api_keys")

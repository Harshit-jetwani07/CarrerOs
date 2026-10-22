"""Add persistent Career Assistant messages.

Revision ID: 20260918_assistant_msgs
Revises: 20260918_builder_consent
"""
from alembic import op
import sqlalchemy as sa

revision = "20260918_assistant_msgs"
down_revision = "20260918_builder_consent"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    if "assistant_messages" not in sa.inspect(bind).get_table_names():
        op.create_table("assistant_messages", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("conversation_id", sa.String(), nullable=False), sa.Column("role", sa.String(), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
        op.create_index("ix_assistant_messages_user_id", "assistant_messages", ["user_id"])
        op.create_index("ix_assistant_messages_conversation_id", "assistant_messages", ["conversation_id"])

def downgrade() -> None:
    if "assistant_messages" in sa.inspect(op.get_bind()).get_table_names(): op.drop_table("assistant_messages")

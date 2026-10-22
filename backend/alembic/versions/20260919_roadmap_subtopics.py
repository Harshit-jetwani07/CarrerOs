"""Add structured study subtopics to roadmap items.

Revision ID: 20260919_roadmap_topics
Revises: 20260919_jd_evidence
"""
from alembic import op
import sqlalchemy as sa

revision = "20260919_roadmap_topics"
down_revision = "20260919_jd_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("roadmap_items")}
    if "subtopics" not in columns:
        op.add_column("roadmap_items", sa.Column("subtopics", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("roadmap_items")}
    if "subtopics" in columns:
        op.drop_column("roadmap_items", "subtopics")

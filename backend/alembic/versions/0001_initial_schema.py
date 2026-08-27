"""Initial schema baseline.

Creates the full schema as it exists after Phases 0-14:
  - users
  - mastery
  - adaptation_events  (with composite index)
  - audit_log
  - pending_adaptations
  - chunks  (with pgvector vector(384) column)

This migration is the single source of truth for the schema.
The old run_migrations() inline runner in database.py has been removed.

Revision ID: 0001
Revises: (none)
Create Date: 2026-08-27
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# ---------------------------------------------------------------------------
# pgvector custom type — allows the migration to run without importing pgvector
# ---------------------------------------------------------------------------
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="student"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # mastery
    # ------------------------------------------------------------------
    op.create_table(
        "mastery",
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("topic_id", sa.String(), nullable=False),
        sa.Column("mastery_level", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("style_preferences", sa.JSON(), nullable=True),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("student_id", "topic_id"),
    )

    # ------------------------------------------------------------------
    # adaptation_events
    # ------------------------------------------------------------------
    op.create_table(
        "adaptation_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("topic_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("signal", sa.String(), nullable=False),
        sa.Column("delta", sa.Float(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_adaptation_events_timestamp", "adaptation_events", ["timestamp"]
    )
    op.create_index(
        "idx_adaptation_student_topic",
        "adaptation_events",
        ["student_id", "topic_id"],
    )

    # ------------------------------------------------------------------
    # audit_log
    # ------------------------------------------------------------------
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("adaptation_event_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("topic_id", sa.String(), nullable=False),
        sa.Column("before_state", sa.JSON(), nullable=True),
        sa.Column("after_state", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["adaptation_event_id"], ["adaptation_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_log_timestamp", "audit_log", ["timestamp"])

    # ------------------------------------------------------------------
    # pending_adaptations
    # ------------------------------------------------------------------
    op.create_table(
        "pending_adaptations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("next_topic_id", sa.String(), nullable=False),
        sa.Column("next_activity_type", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pending_adaptations_created_at", "pending_adaptations", ["created_at"]
    )
    op.create_index(
        "ix_pending_adaptations_student_id", "pending_adaptations", ["student_id"]
    )
    op.create_index(
        "ix_pending_adaptations_status", "pending_adaptations", ["status"]
    )

    # ------------------------------------------------------------------
    # chunks (with pgvector embedding column)
    # ------------------------------------------------------------------
    op.create_table(
        "chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topic_id", sa.String(), nullable=False),
        sa.Column("heading", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "source_type",
            sa.String(),
            nullable=False,
            server_default="handbook",
        ),
        sa.Column("uploaded_by", sa.String(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
        # pgvector column: 384 dimensions for all-MiniLM-L6-v2
        sa.Column("embedding", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chunks_topic_id", "chunks", ["topic_id"])
    op.create_index("ix_chunks_source_type", "chunks", ["source_type"])

    # Use raw SQL for the vector column type since SQLAlchemy doesn't know it
    op.execute("ALTER TABLE chunks ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384)")


def downgrade() -> None:
    op.drop_table("chunks")
    op.drop_table("pending_adaptations")
    op.drop_table("audit_log")
    op.drop_table("adaptation_events")
    op.drop_table("mastery")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")

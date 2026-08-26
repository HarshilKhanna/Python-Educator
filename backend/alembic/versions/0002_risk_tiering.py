"""Phase 20/21 — Risk tiering, monitoring, and kill-switch schema additions.

Adds:
  - adaptation_events.risk_tier column (nullable String)
  - system_settings table (DB-backed kill-switch + runtime config)
  - adaptation_alerts table (anomaly detection flags)

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # adaptation_events — add risk_tier column
    # ------------------------------------------------------------------
    op.add_column(
        "adaptation_events",
        sa.Column("risk_tier", sa.String(), nullable=True),
    )

    # ------------------------------------------------------------------
    # system_settings — DB-backed kill-switch and runtime config store
    # ------------------------------------------------------------------
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("key"),
    )

    # Seed the kill-switch to off (false) so existing deployments are unaffected
    op.execute(
        "INSERT INTO system_settings (key, value) VALUES "
        "('auto_apply_kill_switch', 'false')"
    )

    # ------------------------------------------------------------------
    # adaptation_alerts — anomaly-detection flag table
    # ------------------------------------------------------------------
    op.create_table(
        "adaptation_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("alert_type", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=False),
        sa.Column("resolved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_adaptation_alerts_created_at", "adaptation_alerts", ["created_at"]
    )
    op.create_index(
        "ix_adaptation_alerts_alert_type", "adaptation_alerts", ["alert_type"]
    )
    op.create_index(
        "ix_adaptation_alerts_student_id", "adaptation_alerts", ["student_id"]
    )


def downgrade() -> None:
    op.drop_table("adaptation_alerts")
    op.drop_table("system_settings")
    op.drop_column("adaptation_events", "risk_tier")

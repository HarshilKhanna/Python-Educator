"""
services/monitoring.py — Phase 21

MonitoringService: stats aggregation and heuristic anomaly detection.

Anomaly rules (threshold checks, NOT ML):
  1. Thrashing: a single student receives >= THRASH_COUNT auto-applied
     topic-advancement events within THRASH_WINDOW_MINUTES minutes.
     Likely thrashing or a bug, not real mastery growth.

  2. Rate spike: the count of any auto-apply signal type over the last hour
     is more than RATE_SPIKE_MULTIPLIER × its trailing 7-day hourly average.
     Indicates an unexpected system-wide surge.

Both rules store flags in AdaptationAlert; callers query the alert table to
surface them in the dashboard.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from models import AdaptationEvent, AdaptationAlert


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

THRASH_COUNT: int = 3               # alerts if >= this many advances in window
THRASH_WINDOW_MINUTES: int = 10     # rolling window in minutes

RATE_SPIKE_MULTIPLIER: float = 3.0  # alert if rate > this × 7-day baseline
SPIKE_LOOKBACK_HOURS: int = 1       # "recent" window for spike detection
SPIKE_BASELINE_DAYS: int = 7        # days to compute trailing baseline


# ---------------------------------------------------------------------------
# MonitoringService
# ---------------------------------------------------------------------------

class MonitoringService:
    """Monitoring and anomaly detection for the auto-approval system."""

    # -----------------------------------------------------------------------
    # Stats endpoint data
    # -----------------------------------------------------------------------

    @staticmethod
    async def get_adaptation_stats(
        session: AsyncSession,
        window_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Return counts of auto-applied vs. reviewed adaptations over window_hours,
        broken down by risk tier.

        Returns a dict with:
          total_auto_applied   : int
          total_reviewed       : int  (came through review queue)
          by_tier              : {"low": int, "medium": int, "high": int, None: int}
          window_hours         : int
          since                : ISO timestamp
        """
        since = datetime.now(timezone.utc) - timedelta(hours=window_hours)

        stmt = (
            select(AdaptationEvent)
            .where(
                and_(
                    AdaptationEvent.timestamp >= since,
                    AdaptationEvent.source.in_([
                        "pedagogical_agent_auto",
                        "instructor_review_approval",
                    ]),
                )
            )
        )
        result = await session.execute(stmt)
        events = result.scalars().all()

        auto_applied = [e for e in events if e.source == "pedagogical_agent_auto"]
        reviewed = [e for e in events if e.source == "instructor_review_approval"]

        by_tier: dict[str | None, int] = {}
        for e in auto_applied:
            tier = e.risk_tier
            by_tier[tier] = by_tier.get(tier, 0) + 1

        return {
            "total_auto_applied": len(auto_applied),
            "total_reviewed": len(reviewed),
            "by_tier": {
                "low": by_tier.get("low", 0),
                "medium": by_tier.get("medium", 0),
                "high": by_tier.get("high", 0),
            },
            "window_hours": window_hours,
            "since": since.isoformat(),
        }

    # -----------------------------------------------------------------------
    # Anomaly detection
    # -----------------------------------------------------------------------

    @staticmethod
    async def check_and_store_anomalies(
        session: AsyncSession,
        student_id: str,
        signal_type: str,
    ) -> list[AdaptationAlert]:
        """
        Run heuristic anomaly checks and persist any new alerts.
        Returns the list of newly created AdaptationAlert rows (may be empty).

        Called by tutor.py after each auto-apply; non-fatal — callers must
        handle exceptions so a check failure never blocks the student.
        """
        new_alerts: list[AdaptationAlert] = []

        # Check 1: thrashing
        thrash_alert = await MonitoringService._check_thrashing(
            session, student_id, signal_type
        )
        if thrash_alert:
            session.add(thrash_alert)
            new_alerts.append(thrash_alert)

        # Check 2: rate spike (system-wide)
        spike_alert = await MonitoringService._check_rate_spike(session, signal_type)
        if spike_alert:
            session.add(spike_alert)
            new_alerts.append(spike_alert)

        return new_alerts

    @staticmethod
    async def _check_thrashing(
        session: AsyncSession,
        student_id: str,
        signal_type: str,
    ) -> AdaptationAlert | None:
        """
        Rule 1: flag if a single student receives >= THRASH_COUNT auto-applied
        topic-advancement events within THRASH_WINDOW_MINUTES.
        """
        window_start = datetime.now(timezone.utc) - timedelta(minutes=THRASH_WINDOW_MINUTES)

        stmt = (
            select(AdaptationEvent)
            .where(
                and_(
                    AdaptationEvent.student_id == student_id,
                    AdaptationEvent.source == "pedagogical_agent_auto",
                    AdaptationEvent.signal == signal_type,
                    AdaptationEvent.timestamp >= window_start,
                )
            )
        )
        result = await session.execute(stmt)
        recent = result.scalars().all()

        if len(recent) >= THRASH_COUNT:
            # Check we haven't already open-flagged this student recently
            existing_stmt = (
                select(AdaptationAlert)
                .where(
                    and_(
                        AdaptationAlert.alert_type == "thrashing",
                        AdaptationAlert.student_id == student_id,
                        AdaptationAlert.resolved == 0,
                        AdaptationAlert.created_at >= window_start,
                    )
                )
            )
            existing_result = await session.execute(existing_stmt)
            if existing_result.scalar_one_or_none() is not None:
                return None  # already flagged — don't spam

            return AdaptationAlert(
                alert_type="thrashing",
                student_id=student_id,
                detail={
                    "signal_type": signal_type,
                    "count": len(recent),
                    "window_minutes": THRASH_WINDOW_MINUTES,
                    "threshold": THRASH_COUNT,
                    "event_ids": [e.id for e in recent],
                },
                resolved=0,
            )
        return None

    @staticmethod
    async def _check_rate_spike(
        session: AsyncSession,
        signal_type: str,
    ) -> AdaptationAlert | None:
        """
        Rule 2: flag if auto-apply rate for signal_type over the last hour
        exceeds RATE_SPIKE_MULTIPLIER × its 7-day trailing hourly average.
        """
        now = datetime.now(timezone.utc)
        recent_start = now - timedelta(hours=SPIKE_LOOKBACK_HOURS)
        baseline_start = now - timedelta(days=SPIKE_BASELINE_DAYS)

        # Count recent events (last SPIKE_LOOKBACK_HOURS hours)
        recent_stmt = (
            select(func.count())
            .select_from(AdaptationEvent)
            .where(
                and_(
                    AdaptationEvent.source == "pedagogical_agent_auto",
                    AdaptationEvent.signal == signal_type,
                    AdaptationEvent.timestamp >= recent_start,
                )
            )
        )
        recent_result = await session.execute(recent_stmt)
        recent_count: int = recent_result.scalar_one()

        # Count baseline events (last SPIKE_BASELINE_DAYS days, excluding recent window)
        baseline_stmt = (
            select(func.count())
            .select_from(AdaptationEvent)
            .where(
                and_(
                    AdaptationEvent.source == "pedagogical_agent_auto",
                    AdaptationEvent.signal == signal_type,
                    AdaptationEvent.timestamp >= baseline_start,
                    AdaptationEvent.timestamp < recent_start,
                )
            )
        )
        baseline_result = await session.execute(baseline_stmt)
        baseline_total: int = baseline_result.scalar_one()

        # Convert baseline total to per-hour average
        baseline_hours = SPIKE_BASELINE_DAYS * 24 - SPIKE_LOOKBACK_HOURS
        hourly_baseline = baseline_total / max(baseline_hours, 1)

        # A baseline of 0 means we've never seen this signal — can't spike
        if hourly_baseline == 0:
            return None

        if recent_count > RATE_SPIKE_MULTIPLIER * hourly_baseline:
            # Check for existing open spike alert (don't spam)
            existing_stmt = (
                select(AdaptationAlert)
                .where(
                    and_(
                        AdaptationAlert.alert_type == "rate_spike",
                        AdaptationAlert.student_id.is_(None),
                        AdaptationAlert.resolved == 0,
                        AdaptationAlert.created_at >= recent_start,
                    )
                )
            )
            existing_result = await session.execute(existing_stmt)
            if existing_result.scalar_one_or_none() is not None:
                return None  # already flagged

            return AdaptationAlert(
                alert_type="rate_spike",
                student_id=None,  # system-wide
                detail={
                    "signal_type": signal_type,
                    "recent_count": recent_count,
                    "recent_window_hours": SPIKE_LOOKBACK_HOURS,
                    "hourly_baseline": round(hourly_baseline, 4),
                    "spike_multiplier": RATE_SPIKE_MULTIPLIER,
                    "baseline_days": SPIKE_BASELINE_DAYS,
                },
                resolved=0,
            )
        return None

    # -----------------------------------------------------------------------
    # Alert queries
    # -----------------------------------------------------------------------

    @staticmethod
    async def get_open_alerts(session: AsyncSession) -> list[AdaptationAlert]:
        """Return all unresolved anomaly alerts, newest first."""
        stmt = (
            select(AdaptationAlert)
            .where(AdaptationAlert.resolved == 0)
            .order_by(AdaptationAlert.created_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

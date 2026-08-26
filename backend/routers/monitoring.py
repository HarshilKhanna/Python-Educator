"""
routers/monitoring.py — Phase 21

Monitoring endpoints for the auto-approval system.

GET  /monitoring/stats              — adaptation counts by tier, auto vs reviewed
GET  /monitoring/alerts             — open anomaly alerts
POST /monitoring/alerts/{id}/resolve — mark an alert resolved
GET  /monitoring/kill-switch        — read current kill-switch state
POST /monitoring/kill-switch        — toggle kill-switch (instructor only)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from dependencies import require_role
from models import AdaptationAlert, SystemSettings, User
from services.monitoring import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    total_auto_applied: int
    total_reviewed: int
    by_tier: dict
    window_hours: int
    since: str


class AlertSchema(BaseModel):
    id: int
    created_at: str
    alert_type: str
    student_id: str | None
    detail: dict
    resolved: bool


class KillSwitchResponse(BaseModel):
    active: bool
    source: str  # 'db' | 'env'


class KillSwitchRequest(BaseModel):
    active: bool


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    window_hours: int = 24,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("instructor")),
) -> StatsResponse:
    """
    Return counts of auto-applied vs. reviewed adaptations over window_hours,
    broken down by risk tier.
    """
    stats = await MonitoringService.get_adaptation_stats(db, window_hours=window_hours)
    return StatsResponse(**stats)


@router.get("/alerts", response_model=list[AlertSchema])
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("instructor")),
) -> list[AlertSchema]:
    """Return all open (unresolved) anomaly alerts, newest first."""
    alerts = await MonitoringService.get_open_alerts(db)
    return [
        AlertSchema(
            id=a.id,
            created_at=a.created_at.isoformat() if a.created_at else "",
            alert_type=a.alert_type,
            student_id=a.student_id,
            detail=a.detail or {},
            resolved=bool(a.resolved),
        )
        for a in alerts
    ]


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("instructor")),
) -> dict:
    """Mark an anomaly alert as resolved."""
    stmt = select(AdaptationAlert).where(AdaptationAlert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    if alert.resolved:
        raise HTTPException(status_code=409, detail="Alert is already resolved.")

    alert.resolved = 1
    alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()

    return {"id": alert_id, "resolved": True}


@router.get("/kill-switch", response_model=KillSwitchResponse)
async def get_kill_switch(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("instructor")),
) -> KillSwitchResponse:
    """Read the current kill-switch state (DB setting takes priority over env var)."""
    import config

    stmt = select(SystemSettings).where(SystemSettings.key == "auto_apply_kill_switch")
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()

    if row is not None:
        val = row.value
        active = val is True or str(val).lower() == "true"
        return KillSwitchResponse(active=active, source="db")

    return KillSwitchResponse(active=config.AUTO_APPLY_KILL_SWITCH, source="env")


@router.post("/kill-switch", response_model=KillSwitchResponse)
async def set_kill_switch(
    body: KillSwitchRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("instructor")),
) -> KillSwitchResponse:
    """
    Toggle the kill-switch on or off.

    When active=True, ALL recommendations go to pending_adaptations regardless
    of risk tier — no code deploy required.  This takes effect immediately for
    all subsequent requests.
    """
    stmt = select(SystemSettings).where(SystemSettings.key == "auto_apply_kill_switch")
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()

    if row is None:
        # First time setting — insert
        row = SystemSettings(
            key="auto_apply_kill_switch",
            value=body.active,
        )
        db.add(row)
    else:
        row.value = body.active

    await db.commit()

    return KillSwitchResponse(active=body.active, source="db")

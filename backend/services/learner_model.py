import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Mastery, AdaptationEvent, AuditLog

class LearnerModelService:
    """
    Sole write path to the learner model.
    Enforces validation, creates adaptation events, updates materialized mastery state,
    and records audit logs in a single transaction.
    """

    @staticmethod
    async def record_update(
        session: AsyncSession,
        source: str,
        student_id: str,
        topic_id: str,
        signal: str,
        delta: float,
        risk_tier: str | None = None,
        student_confidence: float | None = None,
    ) -> float:
        """
        Appends an AdaptationEvent, updates the Mastery table, and logs the transaction.
        Returns the new mastery value.

        risk_tier: the risk classification that allowed this write
          ('low' | 'medium' | 'high' | None).  None for events that come through
          the human review queue rather than auto-apply.
        """
        # 1. Fetch current mastery state
        stmt = select(Mastery).where(Mastery.student_id == student_id, Mastery.topic_id == topic_id)
        result = await session.execute(stmt)
        mastery_record = result.scalar_one_or_none()
        
        before_state = None
        if mastery_record:
            before_state = {
                "mastery_level": mastery_record.mastery_level,
                "confidence": mastery_record.confidence,
                "style_preferences": mastery_record.style_preferences
            }
        else:
            # Create a new blank record if none exists
            mastery_record = Mastery(
                student_id=student_id,
                topic_id=topic_id,
                mastery_level=0.0,
                confidence=0.0
            )
            session.add(mastery_record)

        # Apply time decay (forgetting curve) before adding new delta
        if mastery_record.last_updated:
            last_updated = mastery_record.last_updated
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=datetime.timezone.utc)
            days_since = (datetime.datetime.now(datetime.timezone.utc) - last_updated).days
            if days_since > 0:
                # Decay 1% per day, max 20% decay per gap
                decay = min(0.20, days_since * 0.01)
                mastery_record.mastery_level = max(0.0, mastery_record.mastery_level - decay)

        # 2. Enforce logic invariants (e.g. mastery clamped between 0 and 1)
        new_mastery = mastery_record.mastery_level + delta
        new_mastery = max(0.0, min(1.0, new_mastery))
        
        mastery_record.mastery_level = new_mastery
        
        # Update self-reported confidence if the student provided it.
        # Blend: 80% existing confidence + 20% new report to smooth noise.
        if student_confidence is not None:
            blended = 0.8 * mastery_record.confidence + 0.2 * max(0.0, min(1.0, student_confidence))
            mastery_record.confidence = blended
        
        # 3. Create the adaptation event
        event = AdaptationEvent(
            student_id=student_id,
            topic_id=topic_id,
            source=source,
            signal=signal,
            delta=delta,
            risk_tier=risk_tier,
        )
        session.add(event)
        
        # Flush to get the event ID for the audit log
        await session.flush()
        
        after_state = {
            "mastery_level": mastery_record.mastery_level,
            "confidence": mastery_record.confidence,
            "style_preferences": mastery_record.style_preferences
        }
        
        # 4. Create the audit log
        audit = AuditLog(
            adaptation_event_id=event.id,
            student_id=student_id,
            topic_id=topic_id,
            before_state=before_state,
            after_state=after_state
        )
        session.add(audit)
        
        # The caller is responsible for calling await session.commit()
        return new_mastery

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Index, Text
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base


class User(Base):
    """
    Registered user account.

    role: 'student' | 'instructor'
    id is a UUID string used as the canonical student identifier in all
    learner-model tables (Mastery, AdaptationEvent, AuditLog, PendingAdaptation).
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # 'student' | 'instructor'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Mastery(Base):
    """
    Materialized state of the learner model.
    Only updated transactionally alongside AdaptationEvent and AuditLog.
    """
    __tablename__ = "mastery"
    
    student_id = Column(String, primary_key=True)
    topic_id = Column(String, primary_key=True)
    
    # 0.0 to 1.0 (BKT or other KT algorithm estimate)
    mastery_level = Column(Float, nullable=False, default=0.0)
    
    # 0.0 to 1.0 (estimated confidence of the learner on this topic)
    confidence = Column(Float, nullable=False, default=0.0)
    
    # Optional JSON containing style profile info for this topic (e.g. repetition_need)
    style_preferences = Column(JSON, nullable=True)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AdaptationEvent(Base):
    """
    Append-only event log capturing every signal that updates the learner model.
    """
    __tablename__ = "adaptation_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    student_id = Column(String, nullable=False)
    topic_id = Column(String, nullable=False)
    
    # e.g., 'activity_submission', 'instructor_override', 'empathy_classifier'
    source = Column(String, nullable=False)
    
    # e.g., 'correct', 'incorrect', 'hint_used', 'manual_set'
    signal = Column(String, nullable=False)
    
    # The change applied to mastery. e.g., +0.1, -0.05
    delta = Column(Float, nullable=False, default=0.0)
    
    __table_args__ = (
        Index('idx_adaptation_student_topic', 'student_id', 'topic_id'),
    )


class AuditLog(Base):
    """
    Append-only log recording the exact before/after state of the Mastery row
    for explainability and debugging.
    """
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # The event that triggered this change
    adaptation_event_id = Column(Integer, ForeignKey("adaptation_events.id"), nullable=False)
    
    student_id = Column(String, nullable=False)
    topic_id = Column(String, nullable=False)
    
    # JSON representations of the Mastery row
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=False)


class Chunk(Base):
    """
    A chunk of text from the curriculum handbook or an instructor upload.
    """
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(String, nullable=False, index=True)
    heading = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # Source provenance
    # Values: 'handbook' | 'instructor_upload'
    source_type = Column(String, nullable=False, default="handbook", server_default="handbook", index=True)
    uploaded_by = Column(String, nullable=True)   # only set for instructor_upload
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    
    # 384 dimensions for all-MiniLM-L6-v2
    embedding = Column(Vector(384))


class PendingAdaptation(Base):
    """
    Human-in-the-loop review queue (Phase 10).

    When the Pedagogical Agent recommends anything other than 'continue with
    same topic at same difficulty' (i.e. a topic change, remediation branch,
    or difficulty change), the recommendation is written here instead of
    auto-applied.

    Approving an item via POST /review/{id}/approve triggers the actual state
    change through LearnerModelService.record_update as normal.
    """
    __tablename__ = "pending_adaptations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    student_id = Column(String, nullable=False, index=True)

    # The Pedagogical Agent's recommendation
    next_topic_id = Column(String, nullable=False)
    next_activity_type = Column(String, nullable=False)
    reason = Column(String, nullable=False)

    # Status lifecycle: pending → approved | rejected
    status = Column(String, nullable=False, default="pending", index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    # Optional human-readable note from the reviewer (used for rejections)
    review_note = Column(String, nullable=True)


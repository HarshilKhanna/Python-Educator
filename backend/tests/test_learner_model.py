import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from models import Base, Mastery, AdaptationEvent, AuditLog
from services.learner_model import LearnerModelService

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_record_update_creates_mastery_and_logs(db_session: AsyncSession):
    student_id = "student_1"
    topic_id = "loops"
    
    # 1. Initial state: no mastery record
    stmt = select(Mastery).where(Mastery.student_id == student_id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None
    
    # 2. Record an update (+0.2)
    new_mastery = await LearnerModelService.record_update(
        session=db_session,
        source="activity_submission",
        student_id=student_id,
        topic_id=topic_id,
        signal="correct",
        delta=0.2
    )
    await db_session.commit()
    
    assert new_mastery == 0.2
    
    # 3. Verify Mastery table
    stmt = select(Mastery).where(Mastery.student_id == student_id, Mastery.topic_id == topic_id)
    result = await db_session.execute(stmt)
    mastery = result.scalar_one()
    assert mastery.mastery_level == 0.2
    assert mastery.confidence == 0.0
    
    # 4. Verify AdaptationEvent
    stmt = select(AdaptationEvent).where(AdaptationEvent.student_id == student_id)
    result = await db_session.execute(stmt)
    event = result.scalar_one()
    assert event.source == "activity_submission"
    assert event.signal == "correct"
    assert event.delta == 0.2
    
    # 5. Verify AuditLog
    stmt = select(AuditLog).where(AuditLog.adaptation_event_id == event.id)
    result = await db_session.execute(stmt)
    audit = result.scalar_one()
    assert audit.before_state is None
    assert audit.after_state["mastery_level"] == 0.2


@pytest.mark.asyncio
async def test_record_update_clamps_mastery_between_0_and_1(db_session: AsyncSession):
    student_id = "student_2"
    topic_id = "functions"
    
    # Record +1.5 -> should clamp to 1.0
    await LearnerModelService.record_update(db_session, "test", student_id, topic_id, "correct", 1.5)
    await db_session.commit()
    
    stmt = select(Mastery).where(Mastery.student_id == student_id)
    result = await db_session.execute(stmt)
    mastery = result.scalar_one()
    assert mastery.mastery_level == 1.0
    
    # Record -2.0 -> should clamp to 0.0
    await LearnerModelService.record_update(db_session, "test", student_id, topic_id, "incorrect", -2.0)
    await db_session.commit()
    
    stmt = select(Mastery).where(Mastery.student_id == student_id)
    result = await db_session.execute(stmt)
    mastery = result.scalar_one()
    assert mastery.mastery_level == 0.0


@pytest.mark.asyncio
async def test_record_update_audit_log_tracks_changes(db_session: AsyncSession):
    student_id = "student_3"
    topic_id = "lists"
    
    # First update
    await LearnerModelService.record_update(db_session, "t1", student_id, topic_id, "correct", 0.5)
    await db_session.commit()
    
    # Second update
    await LearnerModelService.record_update(db_session, "t2", student_id, topic_id, "incorrect", -0.1)
    await db_session.commit()
    
    stmt = select(AuditLog).where(AuditLog.student_id == student_id).order_by(AuditLog.id.asc())
    result = await db_session.execute(stmt)
    logs = result.scalars().all()
    
    assert len(logs) == 2
    assert logs[0].before_state is None
    assert logs[0].after_state["mastery_level"] == 0.5
    
    assert logs[1].before_state["mastery_level"] == 0.5
    assert logs[1].after_state["mastery_level"] == 0.4

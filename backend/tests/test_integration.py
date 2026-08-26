import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from main import app
from models import Mastery, AdaptationEvent, AuditLog

# conftest.py manages the app.dependency_overrides and table creation.
# We import conftest's shared session factory so our DB assertions hit
# the same in-memory DB that the HTTP layer writes to.
from tests.conftest import _HttpSession


@pytest.mark.asyncio
async def test_post_answer_integration(_setup_http_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        
        # Fetch a real activity from loops.json
        response = await client.get("/activities?topic_id=loops")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) > 0
        
        activity = activities[0]
        act_id = activity["id"]
        correct_ans = activity["correct_answer"]
        incorrect_ans = "some_wrong_answer"
        
        student_id = "integration_student_1"
        
        # --- Correct Answer ---
        res1 = await client.post("/answer", json={
            "student_id": student_id,
            "activity_id": act_id,
            "submitted_answer": correct_ans
        })
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["correct"] is True
        mastery1 = data1["mastery"]
        assert mastery1 > 0.0
        
        # --- Incorrect Answer ---
        res2 = await client.post("/answer", json={
            "student_id": student_id,
            "activity_id": act_id,
            "submitted_answer": incorrect_ans
        })
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["correct"] is False
        mastery2 = data2["mastery"]
        assert mastery2 < mastery1  # Decreased due to wrong answer
        
        # --- DB Verification (same session DB the HTTP layer used) ---
        async with _HttpSession() as session:
            # Verify AdaptationEvent (should be 2)
            stmt = select(AdaptationEvent).where(
                AdaptationEvent.student_id == student_id
            ).order_by(AdaptationEvent.id.asc())
            result = await session.execute(stmt)
            events = result.scalars().all()
            assert len(events) == 2
            assert events[0].signal == "correct"
            assert events[1].signal == "incorrect"
            
            # Verify Mastery table
            stmt = select(Mastery).where(Mastery.student_id == student_id)
            result = await session.execute(stmt)
            mastery = result.scalar_one()
            assert mastery.mastery_level == mastery2
            
            # Verify AuditLog (should be 2)
            stmt = select(AuditLog).where(
                AuditLog.student_id == student_id
            ).order_by(AuditLog.id.asc())
            result = await session.execute(stmt)
            logs = result.scalars().all()
            assert len(logs) == 2
            
            assert logs[0].adaptation_event_id == events[0].id
            assert logs[0].before_state is None
            assert logs[0].after_state["mastery_level"] == mastery1
            
            assert logs[1].adaptation_event_id == events[1].id
            assert logs[1].before_state["mastery_level"] == mastery1
            assert logs[1].after_state["mastery_level"] == mastery2


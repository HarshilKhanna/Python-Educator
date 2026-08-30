import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

_BACKEND = Path(__file__).parent
sys.path.insert(0, str(_BACKEND))

from database import AsyncSessionLocal
from models import User, Mastery, AdaptationEvent, PendingAdaptation, SystemSettings, AdaptationAlert
from auth import hash_password

async def generate_mock_data():
    print("[mock] Starting mock dashboard data generation...")
    async with AsyncSessionLocal() as session:
        # Clear existing students and pending items, cascading carefully
        await session.execute(text("DELETE FROM audit_log;"))
        await session.execute(text("DELETE FROM pending_adaptations;"))
        await session.execute(text("DELETE FROM adaptation_alerts;"))
        await session.execute(text("DELETE FROM adaptation_events;"))
        await session.execute(text("DELETE FROM mastery;"))
        await session.execute(text("DELETE FROM users WHERE role='student';"))
        await session.commit()
        
        students = [
            {"email": "slow_learner_1@school.edu", "mastery": 0.3, "confidence": 0.4},
            {"email": "ahead_learner_2@school.edu", "mastery": 0.8, "confidence": 0.9},
            {"email": "struggling_learner_3@school.edu", "mastery": 0.1, "confidence": 0.8},
        ]
        
        user_ids = []
        for s in students:
            user = User(email=s["email"], password_hash=hash_password("student123"), role="student")
            session.add(user)
            await session.commit()
            await session.refresh(user)
            user_ids.append(user.id)
            print(f"[mock] Created student {user.email}")

            mastery = Mastery(
                student_id=user.id,
                topic_id="loops",
                mastery_level=s["mastery"],
                confidence=s["confidence"]
            )
            session.add(mastery)
            
            event = AdaptationEvent(
                student_id=user.id,
                topic_id="loops",
                source="auto_pedagogical_agent",
                signal="struggled_on_for_loops",
                delta=-0.05,
                risk_tier="low"
            )
            session.add(event)
            await session.commit()

        pending_1 = PendingAdaptation(
            student_id=user_ids[0],
            next_topic_id="conditionals",
            next_activity_type="remediation",
            reason="Student has failed 4 loops tasks consecutively. High frustration detected. Recommending branching back to conditionals.",
            status="pending"
        )
        pending_2 = PendingAdaptation(
            student_id=user_ids[2],
            next_topic_id="lists",
            next_activity_type="predict_output",
            reason="Student claims high confidence but exhibits low mastery on loops. Recommending a hard gate via predict_output before advancing.",
            status="pending"
        )
        session.add_all([pending_1, pending_2])
        await session.commit()

        try:
            kill_switch = SystemSettings(
                key="auto_apply_kill_switch",
                value={"enabled": False}
            )
            session.add(kill_switch)
            await session.commit()
        except Exception:
            await session.rollback()
            pass
        
        alert = AdaptationAlert(
            alert_type="thrashing",
            student_id=user_ids[0],
            detail={"message": "System detected 3 consecutive auto-downgrades in 5 minutes."},
            resolved=0
        )
        session.add(alert)
        await session.commit()
        
        print("[mock] SUCCESSFULLY POPULATED! You can check the dashboard now.")

if __name__ == "__main__":
    asyncio.run(generate_mock_data())

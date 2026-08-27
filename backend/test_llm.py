import asyncio
import traceback
from agents.technical import technical_agent_node
from database import AsyncSessionLocal

async def main():
    try:
        async with AsyncSessionLocal() as session:
            res = await technical_agent_node(
                question="What are loops?", 
                topic_id="loops", 
                session=session
            )
            print("Response:", res)
    except Exception as e:
        print("EXCEPTION OCCURRED:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

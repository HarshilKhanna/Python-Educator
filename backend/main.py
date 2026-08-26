import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import activities, answers
from routers.auth import router as auth_router
from routers.tutor import router as tutor_router
from routers.review import router as review_router
from routers.materials import router as materials_router
from routers.students import router as students_router

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Dispose engine on shutdown
    await engine.dispose()

app = FastAPI(
    title="Python Educator API",
    description="Agentic Python tutoring backend",
    version="0.1.0",
    lifespan=lifespan
)

# Allow Flutter web / local emulators to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(activities.router)
app.include_router(answers.router)
app.include_router(tutor_router)
app.include_router(review_router)
app.include_router(materials_router)
app.include_router(students_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health-check endpoint — returns service status."""
    return {"status": "ok", "service": "python-educator-api"}

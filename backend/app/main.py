from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, profile, resume, career, skills, roadmap, jobs, dashboard, settings as settings_router, resume_builder, assistant

# Auto-create tables in dev. In production, use `alembic upgrade head` instead
# and remove this line — migrations are the source of truth there.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CareerOS API",
    description="AI-powered career intelligence platform — resume analysis, "
                 "career matching, skill-gap detection, and personalized roadmaps.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    # Next may choose 3001 when another local app already owns 3000. Permit
    # the two normal local development hosts without opening production CORS.
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):(3000|3001)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(resume.router)
app.include_router(career.router)
app.include_router(skills.router)
app.include_router(roadmap.router)
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(settings_router.router)
app.include_router(resume_builder.router)
app.include_router(assistant.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}

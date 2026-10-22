from pydantic import BaseModel, Field


class RoadmapItemOut(BaseModel):
    id: int
    week_number: int
    topic: str
    why_needed: str | None
    current_level: str | None
    target_level: str | None
    estimated_days: int
    practice_task: str | None
    project_suggestion: str | None
    subtopics: list[str] | None = None
    resources: str | None
    completed: bool

    class Config:
        from_attributes = True


class RoadmapOut(BaseModel):
    id: int
    role_name: str
    total_weeks: int
    items: list[RoadmapItemOut]
    weekly_study_hours: int

    class Config:
        from_attributes = True


class RoadmapGenerateRequest(BaseModel):
    role_name: str
    total_weeks: int = Field(default=8, ge=4, le=16)

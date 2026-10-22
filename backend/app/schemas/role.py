from pydantic import BaseModel


class RoleMatch(BaseModel):
    role_name: str
    match_percent: int
    breakdown: dict  # {"skill_match": 45, "project_evidence": 15, ...} contributions


class SkillGapItem(BaseModel):
    skill: str
    priority: str  # HIGH / MEDIUM / LOW
    user_level: int
    required_level: int
    status: str


class SkillGapOut(BaseModel):
    role_name: str
    matched_skills: list[str]
    gaps: list[SkillGapItem]

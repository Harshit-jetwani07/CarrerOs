from pydantic import BaseModel


class JDRequirementOut(BaseModel):
    label: str
    status: str
    weight: int
    evidence: str


class JDAnalyzeRequest(BaseModel):
    title: str | None = None
    raw_text: str


class JDAnalyzeOut(BaseModel):
    id: int
    title: str | None
    extracted_skills: list[str]
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    requirement_breakdown: list[JDRequirementOut] = []
    recommendation: str | None

    class Config:
        from_attributes = True

from pydantic import BaseModel


class BulletRewrite(BaseModel):
    before: str
    after: str


class ResumeAnalysisOut(BaseModel):
    overall_score: int
    ats_score: int
    category_scores: dict
    parsed_profile: dict
    strengths: list[str]
    weaknesses: list[str]
    bullet_rewrites: list[BulletRewrite]

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: int
    filename: str
    analysis: ResumeAnalysisOut | None = None

    class Config:
        from_attributes = True

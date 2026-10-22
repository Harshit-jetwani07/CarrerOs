from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_text = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resumes")
    analysis = relationship("ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")


class ResumeAnalysis(Base):
    """AI-generated structured analysis of a resume, stored as JSON."""
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    overall_score = Column(Integer, default=0)
    ats_score = Column(Integer, default=0)

    # Structured JSON blobs — see schemas/resume.py for the shape.
    category_scores = Column(JSON, default=dict)     # {"skills": 82, "projects": 76, ...}
    parsed_profile = Column(JSON, default=dict)       # education/skills/projects/experience/...
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    bullet_rewrites = Column(JSON, default=list)      # [{"before": "...", "after": "..."}]

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="analysis")

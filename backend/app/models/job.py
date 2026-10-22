from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base


class JobDescription(Base):
    """A JD the user pasted in, plus its AI-extracted requirements + match result."""
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    raw_text = Column(String, nullable=False)

    extracted_skills = Column(JSON, default=list)   # ["Python", "AWS", ...]
    match_score = Column(Integer, default=0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    # Requirement-level evidence: [{label, status, weight, evidence}].
    # This prevents a single broad keyword from incorrectly producing 100%.
    requirement_breakdown = Column(JSON, default=list)
    recommendation = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

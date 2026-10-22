from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, Text, func

from app.database import Base


class ResumeDraft(Base):
    """Editable source data for the builder; separate from immutable uploads."""
    __tablename__ = "resume_drafts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    personal_info = Column(JSON, default=dict)
    summary = Column(Text, nullable=True)
    education = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    achievements = Column(JSON, default=list)
    # Builder content becomes dashboard evidence only after explicit user consent.
    use_for_overview = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

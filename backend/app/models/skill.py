from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=True)  # language / framework / tool / concept


class UserSkill(Base):
    """A skill a user has, with a proficiency score 0-100."""
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency = Column(Float, default=0)  # 0-100
    evidence_source = Column(String, nullable=True)  # "resume" / "manual" / "github"

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")

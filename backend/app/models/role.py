from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Role(Base):
    """A target career role, e.g. 'Backend Developer'."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    required_skills = relationship("RoleSkill", back_populates="role", cascade="all, delete-orphan")


class RoleSkill(Base):
    """A skill required for a role, with an importance weight 0-1."""
    __tablename__ = "role_skills"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    importance = Column(Float, default=1.0)  # 0-1, used in gap priority

    role = relationship("Role", back_populates="required_skills")
    skill = relationship("Skill")

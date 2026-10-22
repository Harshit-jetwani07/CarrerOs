from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    total_weeks = Column(Integer, default=8)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="roadmaps")
    role = relationship("Role")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapItem.week_number")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    topic = Column(String, nullable=False)
    why_needed = Column(String, nullable=True)
    current_level = Column(String, nullable=True)
    target_level = Column(String, nullable=True)
    estimated_days = Column(Integer, default=5)
    practice_task = Column(String, nullable=True)
    project_suggestion = Column(String, nullable=True)
    subtopics = Column(JSON, default=list)
    resources = Column(String, nullable=True)  # newline-separated links, kept simple
    completed = Column(Boolean, default=False)

    roadmap = relationship("Roadmap", back_populates="items")

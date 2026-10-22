from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from app.database import Base


class AssistantMessage(Base):
    __tablename__ = "assistant_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
